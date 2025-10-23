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
        "team_id": u.team.id if u.team else None,
        "created_at": make_naive(u.created_at),
        "updated_at": make_naive(u.updated_at)
    } for u in db.query(models.User).all()])

    # Teams
    df_teams = pd.DataFrame([{
        "id": int(t.id),
        "name": t.name,
        "created_at": make_naive(t.created_at)
    } for t in db.query(models.Team).all()])

    # Roles
    df_roles = pd.DataFrame([{
        "id": int(r.id),
        "name": r.name,
        "description": r.description,
        "created_at": make_naive(r.created_at),
        "updated_at": make_naive(r.updated_at)
    } for r in db.query(models.Role).all()])
    df_roles.to_excel(writer, sheet_name="Roles", index=False)

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
        "parent_id": s.parent_id,
        "created_at": make_naive(s.created_at),
        "updated_at": make_naive(s.updated_at)
    } for s in db.query(models.Session).all()])

    # Session-Criterion Associations
    df_session_criteria = pd.DataFrame([{
        "session_id": sc.session_id,
        "criterion_id": sc.criterion_id,
        "role_id": sc.role_id,
        "weight": sc.weight
    } for sc in db.query(models.SessionCriterion).all()])

    # User-Criteria
    df_user_criteria = pd.DataFrame([{
        "id": uc.id,
        "user_id": uc.user_id,
        "criterion_id": uc.criterion_id,
        "session_id": uc.session_id,
        "count_value": uc.count_value,
        "is_fulfilled": uc.is_fulfilled,
        "active_text": uc.active_text,
        "created_at": make_naive(uc.created_at),
        "updated_at": make_naive(uc.updated_at)
    } for uc in db.query(models.UserCriterion).all()])

    # Save all DataFrames to Excel workbook in memory
    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df_users.to_excel(writer, sheet_name="Users", index=False)
        df_teams.to_excel(writer, sheet_name="Teams", index=False)
        df_criteria.to_excel(writer, sheet_name="Criteria", index=False)
        df_sessions.to_excel(writer, sheet_name="Sessions", index=False)
        df_session_criteria.to_excel(writer, sheet_name="SessionCriteria", index=False)
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
        team_id_map = {}
        role_id_map = {}
        criterion_id_map = {}
        session_id_map = {}

        # --- 1. TEAMS ---
        if "Teams" in xls.sheet_names:
            df_teams = pd.read_excel(xls, sheet_name="Teams")
            for _, row in df_teams.iterrows():
                existing = db.query(models.Team).filter_by(name=row["name"]).first()
                if existing:
                    team_id_map[int(row["id"])] = existing.id
                    continue
                new_team = models.Team(
                    name=row["name"]
                )
                db.add(new_team)
                db.flush()
                team_id_map[int(row["id"])] = new_team.id
            db.commit()

        # --- 2. ROLES ---
        if "Roles" in xls.sheet_names:
            df_roles = pd.read_excel(xls, sheet_name="Roles")
            role_id_map = {}
            for _, row in df_roles.iterrows():
                existing = db.query(models.Role).filter_by(name=row["name"]).first()
                if existing:
                    role_id_map[int(row["id"])] = existing.id
                    continue
                new_role = models.Role(
                    name=row["name"],
                    description=row.get("description")
                )
                db.add(new_role)
                db.flush()
                role_id_map[int(row["id"])] = new_role.id
            db.commit()

        # --- 3. USERS ---
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
                    password_hash=row.get("password_hash") or hash_password("test"),
                    team_id=team_id_map.get(int(row["team_id"])) if not pd.isna(row.get("team_id")) else None
                )
                db.add(new_user)
                db.flush()
                user_id_map[int(row["id"])] = new_user.id
            db.commit()

        # --- 4. CRITERIA ---
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

        # --- 5. SESSIONS ---
        if "Sessions" in xls.sheet_names:
            df_sessions = pd.read_excel(xls, sheet_name="Sessions")
            for _, row in df_sessions.iterrows():
                parent_ref = session_id_map.get(int(row["parent_id"])) if not pd.isna(row.get("parent_id")) else None
                existing = db.query(models.Session).filter_by(title=row["title"], parent_id=parent_ref).first()
                if existing:
                    session_id_map[int(row["id"])] = existing.id
                    continue
                new_s = models.Session(
                    title=row["title"],
                    description=row.get("description"),
                    parent_id=parent_ref
                )
                db.add(new_s)
                db.flush()
                session_id_map[int(row["id"])] = new_s.id
            db.commit()  # commit sessions

        # --- 6. SESSION-CRITERIA ASSOCIATIONS ---
        if "SessionCriteria" in xls.sheet_names:
            df_sc = pd.read_excel(xls, sheet_name="SessionCriteria")
            for _, row in df_sc.iterrows():
                session_ref = session_id_map[int(row["session_id"])]
                criterion_ref = criterion_id_map[int(row["criterion_id"])]
                role_ref = role_id_map.get(int(row["role_id"])) if not pd.isna(row.get("role_id")) else None
                existing = db.query(models.SessionCriterion).filter_by(
                    session_id=session_ref, criterion_id=criterion_ref, role_id=role_ref
                ).first()
                if existing:
                    continue
                db.add(models.SessionCriterion(
                    session_id=session_ref,
                    criterion_id=criterion_ref,
                    role_id=role_ref,
                    weight=int(row.get("weight", 1))
                ))
            db.commit()

        # --- 7. USER-CRITERIA ---
        if "UserCriteria" in xls.sheet_names:
            df_uc = pd.read_excel(xls, sheet_name="UserCriteria")
            for _, row in df_uc.iterrows():
                user_ref = user_id_map[int(row["user_id"])]
                criterion_ref = criterion_id_map[int(row["criterion_id"])]
                session_ref = session_id_map.get(int(row["session_id"])) if not pd.isna(row.get("session_id")) else None
                existing = db.query(models.UserCriterion).filter_by(
                    user_id=user_ref, criterion_id=criterion_ref, session_id=session_ref
                ).first()
                if existing:
                    # Update active_text if exists
                    if row.get("active_text"):
                        db.add(models.UserCriterionText(
                            user_criterion_id=existing.id,
                            text_value=row["active_text"],
                            is_active=True
                        ))
                    continue
                new_uc = models.UserCriterion(
                    user_id=user_ref,
                    criterion_id=criterion_ref,
                    session_id=session_ref,
                    count_value=int(row.get("count_value", 0)),
                    is_fulfilled=bool(row.get("is_fulfilled", False))
                )
                db.add(new_uc)
                db.flush()
                # Add active text
                if row.get("active_text"):
                    db.add(models.UserCriterionText(
                        user_criterion_id=new_uc.id,
                        text_value=row["active_text"],
                        is_active=True
                    ))
            db.commit()

        return {"message": "Import completed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing Excel file: {str(e)}")
