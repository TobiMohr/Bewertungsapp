from fastapi import APIRouter, Depends, Response, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from datetime import datetime

from .. import db, models
from ..security import hash_password  # for default passwords on users

router = APIRouter(prefix="/files", tags=["files"])

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# -------------------------
# EXPORT ALL MODELS TO XLSX
# -------------------------
@router.get("/export")
def export_all_xlsx(db: Session = Depends(get_db)):
    def make_naive(dt):
        if dt is None:
            return None
        if hasattr(dt, "tzinfo") and dt.tzinfo is not None:
            return dt.replace(tzinfo=None)
        return dt

    # Users
    df_users = pd.DataFrame([{
        "id": int(u.id),
        "first_name": u.first_name,
        "last_name": u.last_name,
        "email": u.email,
        "password_hash": u.password_hash,
        "created_at": make_naive(u.created_at),
        "updated_at": make_naive(u.updated_at)
    } for u in db.query(models.User).all()])

    # Criteria
    df_criteria = pd.DataFrame([{
        "id": int(c.id),
        "name": c.name,
        "type": c.type.value,
        "created_at": make_naive(c.created_at),
        "updated_at": make_naive(c.updated_at)
    } for c in db.query(models.Criterion).all()])

    # Sessions
    df_sessions = pd.DataFrame([{
        "id": int(s.id),
        "title": s.title,
        "description": s.description,
        "created_at": make_naive(s.created_at),
        "updated_at": make_naive(s.updated_at)
    } for s in db.query(models.Session).all()])

    # Phases
    df_phases = pd.DataFrame([{
        "id": int(p.id),
        "title": p.title,
        "description": p.description,
        "session_id": int(p.session_id),
        "parent_id": int(p.parent_id) if p.parent_id else None,
        "created_at": make_naive(p.created_at),
        "updated_at": make_naive(p.updated_at)
    } for p in db.query(models.Phase).all()])

    # Phase-Criteria associations
    df_phase_criteria = pd.DataFrame([{
        "phase_id": int(pc.phase_id),
        "criterion_id": int(pc.criterion_id),
        "weight": int(pc.weight)
    } for pc in db.query(models.PhaseCriterion).all()])

    # User-Criteria
    df_user_criteria = pd.DataFrame([{
        "user_id": int(uc.user_id),
        "criterion_id": int(uc.criterion_id),
        "phase_id": int(uc.phase_id) if uc.phase_id is not None else None,
        "count_value": int(uc.count_value),
        "is_fulfilled": bool(uc.is_fulfilled),
        "text_value": uc.text_value
    } for uc in db.query(models.UserCriterion).all()])

    # Save all DataFrames to Excel workbook in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_users.to_excel(writer, sheet_name="Users", index=False)
        df_criteria.to_excel(writer, sheet_name="Criteria", index=False)
        df_sessions.to_excel(writer, sheet_name="Sessions", index=False)
        df_phases.to_excel(writer, sheet_name="Phases", index=False)
        df_phase_criteria.to_excel(writer, sheet_name="PhaseCriteria", index=False)
        df_user_criteria.to_excel(writer, sheet_name="UserCriteria", index=False)

    output.seek(0)
    return Response(
        content=output.read(),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=export.xlsx"}
    )


# -------------------------
# IMPORT ALL MODELS FROM XLSX
# -------------------------
@router.post("/import")
async def import_all_xlsx(file: UploadFile = File(...), db: Session = Depends(get_db)):
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload an Excel file.")

    try:
        contents = await file.read()
        xls = pd.ExcelFile(BytesIO(contents))

        # Track mapping from old IDs to new IDs (if needed)
        user_id_map = {}
        criterion_id_map = {}
        session_id_map = {}
        phase_id_map = {}

        # --- 1. USERS ---
        if "Users" in xls.sheet_names:
            df_users = pd.read_excel(xls, sheet_name="Users")
            for _, row in df_users.iterrows():
                existing = db.query(models.User).filter_by(email=row["email"]).first()
                if existing:
                    user_id_map[int(row["id"])] = existing.id
                    continue
                new_user = models.User(
                    first_name=row["first_name"],
                    last_name=row["last_name"],
                    email=row["email"],
                    password_hash=row.get("password_hash") or hash_password("test")
                )
                db.add(new_user)
                db.flush()
                user_id_map[int(row["id"])] = new_user.id
            db.commit()  # commit users first

        # --- 2. CRITERIA ---
        if "Criteria" in xls.sheet_names:
            df_criteria = pd.read_excel(xls, sheet_name="Criteria")
            for _, row in df_criteria.iterrows():
                existing = (
                    db.query(models.Criterion)
                    .filter_by(name=row["name"], type=row["type"])
                    .first()
                )
                if existing:
                    criterion_id_map[int(row["id"])] = existing.id
                    continue
                new_c = models.Criterion(
                    name=row["name"],
                    type=row["type"]
                )
                db.add(new_c)
                db.flush()
                criterion_id_map[int(row["id"])] = new_c.id
            db.commit()  # commit criteria

        # --- 3. SESSIONS ---
        if "Sessions" in xls.sheet_names:
            df_sessions = pd.read_excel(xls, sheet_name="Sessions")
            for _, row in df_sessions.iterrows():
                description = row.get("description")
                if pd.isna(description):
                    description = None

                existing = (
                    db.query(models.Session)
                    .filter_by(title=row["title"], description=description)
                    .first()
                )
                if existing:
                    session_id_map[int(row["id"])] = existing.id
                    continue
                new_s = models.Session(
                    title=row["title"],
                    description=description
                )
                db.add(new_s)
                db.flush()
                session_id_map[int(row["id"])] = new_s.id
            db.commit()  # commit sessions

        # --- 4. PHASES ---
        if "Phases" in xls.sheet_names:
            df_phases = pd.read_excel(xls, sheet_name="Phases")
            for _, row in df_phases.iterrows():
                session_ref = session_id_map[int(row["session_id"])]
                parent_ref = phase_id_map.get(int(row["parent_id"])) if not pd.isna(row.get("parent_id")) else None
                description = row.get("description")
                if pd.isna(description):
                    description = None

                existing = db.query(models.Phase).filter_by(title=row["title"], session_id=session_ref, parent_id=parent_ref, description=description).first()
                if existing:
                    phase_id_map[int(row["id"])] = existing.id
                    continue
                new_p = models.Phase(
                    title=row["title"],
                    description=description,
                    session_id=session_ref,
                    parent_id=parent_ref
                )
                db.add(new_p)
                db.flush()
                phase_id_map[int(row["id"])] = new_p.id
            db.commit()


        # --- 5. PHASE-CRITERIA ASSOCIATIONS ---
        if "PhaseCriteria" in xls.sheet_names:
            df_pc = pd.read_excel(xls, sheet_name="PhaseCriteria")
            for _, row in df_pc.iterrows():

                existing = db.query(models.PhaseCriterion).filter_by(
                    phase_id=phase_id_map[int(row["phase_id"])],
                    criterion_id=criterion_id_map[int(row["criterion_id"])]
                ).first()

                if existing:
                    continue
                db.add(models.PhaseCriterion(
                    phase_id=phase_id_map[int(row["phase_id"])],
                    criterion_id=criterion_id_map[int(row["criterion_id"])],
                    weight=int(row.get("weight", 1))
                ))
            db.commit()  # commit phase-criteria

        # --- 6. USER-CRITERIA ---
        if "UserCriteria" in xls.sheet_names:
            df_uc = pd.read_excel(xls, sheet_name="UserCriteria")
            # Convert types to avoid numpy issues
            df_uc["user_id"] = df_uc["user_id"].astype(int).map(user_id_map)
            df_uc["criterion_id"] = df_uc["criterion_id"].astype(int).map(criterion_id_map)
            df_uc["phase_id"] = df_uc["phase_id"].apply(lambda x: int(x) if not pd.isna(x) else None).map(phase_id_map)
            df_uc["count_value"] = df_uc["count_value"].fillna(0).astype(int)
            df_uc["is_fulfilled"] = df_uc["is_fulfilled"].fillna(False).astype(bool)
            df_uc["text_value"] = df_uc["text_value"].astype(str).replace("nan", None)

            for _, row in df_uc.iterrows():
                existing = db.query(models.UserCriterion).filter_by(
                    user_id=row["user_id"],
                    criterion_id=row["criterion_id"],
                    phase_id=row["phase_id"]
                ).first()

                if existing:
                    continue
                db.add(models.UserCriterion(
                    user_id=row["user_id"],
                    criterion_id=row["criterion_id"],
                    phase_id=row["phase_id"],
                    count_value=row["count_value"],
                    is_fulfilled=row["is_fulfilled"],
                    text_value=row["text_value"]
                ))
            db.commit()  # commit user-criteria

        return {"message": "Import completed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing Excel file: {str(e)}")
