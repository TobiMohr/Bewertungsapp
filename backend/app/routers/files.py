from fastapi import APIRouter, Depends, Response, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO
from datetime import datetime
from sqlalchemy import text

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

    # User-Session Roles
    df_user_session_roles = pd.DataFrame([{
        "id": usr.id,
        "user_id": usr.user_id,
        "session_id": usr.session_id,
        "role_id": usr.role_id,
        "created_at": make_naive(usr.created_at),
        "updated_at": make_naive(usr.updated_at)
    } for usr in db.query(models.UserSessionRole).all()])

    # UserCriterionText
    df_uc_texts = pd.DataFrame([{
        "id": t.id,
        "user_criterion_id": t.user_criterion_id,
        "text_value": t.text_value,
        "is_active": t.is_active,
        "created_at": make_naive(t.created_at)
    } for t in db.query(models.UserCriterionText).all()])

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
        df_roles.to_excel(writer, sheet_name="Roles", index=False)
        df_criteria.to_excel(writer, sheet_name="Criteria", index=False)
        df_sessions.to_excel(writer, sheet_name="Sessions", index=False)
        df_session_criteria.to_excel(writer, sheet_name="SessionCriteria", index=False)
        df_user_session_roles.to_excel(writer, sheet_name="UserSessionRoles", index=False)
        df_uc_texts.to_excel(writer, sheet_name="UserCriterionTexts", index=False)
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
                team = db.query(models.Team).filter_by(name=row["name"]).first()
                if team:
                    # Update if needed
                    team.name = row["name"]
                    team_id_map[int(row["id"])] = team.id
                else:
                    team = models.Team(id=int(row["id"]), name=row["name"])
                    db.add(team)
                    db.flush()
                    team_id_map[int(row["id"])] = team.id
            db.commit()

        # --- 2. ROLES ---
        if "Roles" in xls.sheet_names:
            df_roles = pd.read_excel(xls, sheet_name="Roles")
            for _, row in df_roles.iterrows():
                role = db.query(models.Role).filter_by(name=row["name"]).first()
                if role:
                    role.description = row.get("description") if not pd.isna(row.get("description")) else None
                    role_id_map[int(row["id"])] = role.id
                else:
                    role = models.Role(id=int(row["id"]), name=row["name"], description=row.get("description"))
                    db.add(role)
                    db.flush()
                    role_id_map[int(row["id"])] = role.id
            db.commit()

        # --- 3. USERS ---
        if "Users" in xls.sheet_names:
            df_users = pd.read_excel(xls, sheet_name="Users")
            for _, row in df_users.iterrows():
                user = db.query(models.User).filter_by(email=row["email"]).first()
                if user:
                    # Update fields
                    user.first_name = row["first_name"]
                    user.last_name = row["last_name"]
                    user.team_id = team_id_map.get(int(row["team_id"])) if not pd.isna(row.get("team_id")) else None
                    user_id_map[int(row["id"])] = user.id
                else:
                    user = models.User(
                        id=int(row["id"]),
                        first_name=row["first_name"],
                        last_name=row["last_name"],
                        email=row["email"],
                        password_hash=row.get("password_hash") or hash_password("test"),
                        team_id=team_id_map.get(int(row["team_id"])) if not pd.isna(row.get("team_id")) else None
                    )
                    db.add(user)
                    db.flush()
                    user_id_map[int(row["id"])] = user.id
            db.commit()

        # --- 4. CRITERIA ---
        if "Criteria" in xls.sheet_names:
            df_criteria = pd.read_excel(xls, sheet_name="Criteria")
            for _, row in df_criteria.iterrows():
                criterion = db.query(models.Criterion).filter_by(name=row["name"], type=row["type"]).first()
                if criterion:
                    # Update if needed
                    criterion.name = row["name"]
                    criterion.type = row["type"]
                    criterion_id_map[int(row["id"])] = criterion.id
                else:
                    criterion = models.Criterion(id=int(row["id"]), name=row["name"], type=row["type"])
                    db.add(criterion)
                    db.flush()
                    criterion_id_map[int(row["id"])] = criterion.id
            db.commit()

        # --- 5. SESSIONS ---
        if "Sessions" in xls.sheet_names:
            df_sessions = pd.read_excel(xls, sheet_name="Sessions")
            for _, row in df_sessions.iterrows():
                parent_ref = session_id_map.get(int(row["parent_id"])) if not pd.isna(row.get("parent_id")) else None
                session = db.query(models.Session).filter_by(title=row["title"], parent_id=parent_ref).first()
                if session:
                    session.description = row.get("description")
                    session.parent_id = parent_ref
                    session_id_map[int(row["id"])] = session.id
                else:
                    session = models.Session(
                        id=int(row["id"]),
                        title=row["title"],
                        description=row.get("description"),
                        parent_id=parent_ref
                    )
                    db.add(session)
                    db.flush()
                    session_id_map[int(row["id"])] = session.id
            db.commit()

        # --- 6. SESSION-CRITERIA ASSOCIATIONS ---
        if "SessionCriteria" in xls.sheet_names:
            df_sc = pd.read_excel(xls, sheet_name="SessionCriteria")
            for _, row in df_sc.iterrows():
                session_ref = session_id_map[int(row["session_id"])]
                criterion_ref = criterion_id_map[int(row["criterion_id"])]
                role_ref = role_id_map.get(int(row["role_id"])) if not pd.isna(row.get("role_id")) else None
                assoc = db.query(models.SessionCriterion).filter_by(
                    session_id=session_ref, criterion_id=criterion_ref, role_id=role_ref
                ).first()
                if assoc:
                    assoc.weight = int(row.get("weight", 1))
                else:
                    assoc = models.SessionCriterion(
                        session_id=session_ref,
                        criterion_id=criterion_ref,
                        role_id=role_ref,
                        weight=int(row.get("weight", 1))
                    )
                    db.add(assoc)
            db.commit()

        # --- 7. USER-CRITERION TEXTS ---
        if "UserCriterionTexts" in xls.sheet_names:
            df_uc_texts = pd.read_excel(xls, sheet_name="UserCriterionTexts")
            
            for _, row in df_uc_texts.iterrows():
                user_criterion_ref = db.query(models.UserCriterion).get(row["user_criterion_id"])
                if not user_criterion_ref:
                    continue 

                text_value = row["text_value"]
                if pd.isna(text_value):
                    text_value = ""

                # Check if ID already exists in DB
                uct = db.query(models.UserCriterionText).get(int(row["id"]))
                if uct:
                    uct.user_criterion_id = user_criterion_ref.id
                    uct.text_value = text_value
                    uct.is_active = row["is_active"]
                    uct.created_at = row.get("created_at") or uct.created_at
                else:
                    db.add(models.UserCriterionText(
                        id=int(row["id"]),
                        user_criterion_id=user_criterion_ref.id,
                        text_value=text_value,
                        is_active=row["is_active"],
                        created_at=row.get("created_at") or datetime.now().isoformat()
                    ))

            db.commit()

        # --- USER-SESSION ROLES ---
        if "UserSessionRoles" in xls.sheet_names:
            df_usr_roles = pd.read_excel(xls, sheet_name="UserSessionRoles")
            for _, row in df_usr_roles.iterrows():
                user_ref = user_id_map[int(row["user_id"])]
                session_ref = session_id_map[int(row["session_id"])]
                role_ref = role_id_map[int(row["role_id"])]

                usr_role = db.query(models.UserSessionRole).filter_by(
                    user_id=user_ref, session_id=session_ref, role_id=role_ref
                ).first()

                if usr_role:
                    usr_role.updated_at = row.get("updated_at") or usr_role.updated_at
                else:
                    db.add(models.UserSessionRole(
                        id=int(row["id"]),
                        user_id=user_ref,
                        session_id=session_ref,
                        role_id=role_ref,
                        created_at=row.get("created_at") or datetime.now().isoformat(),
                        updated_at=row.get("updated_at") or datetime.now().isoformat()
                    ))
            db.commit()

        # --- USER-CRITERIA ---
        if "UserCriteria" in xls.sheet_names:
            df_uc = pd.read_excel(xls, sheet_name="UserCriteria")
            for _, row in df_uc.iterrows():
                user_ref = user_id_map[int(row["user_id"])]
                criterion_ref = criterion_id_map[int(row["criterion_id"])]
                session_ref = session_id_map.get(int(row["session_id"])) if not pd.isna(row.get("session_id")) else None
                uc = db.query(models.UserCriterion).filter_by(
                    user_id=user_ref, criterion_id=criterion_ref, session_id=session_ref
                ).first()

                if uc:
                    uc.count_value = int(row.get("count_value", 0))
                    uc.is_fulfilled = bool(row.get("is_fulfilled", False))
                else:
                    uc = models.UserCriterion(
                        user_id=user_ref,
                        criterion_id=criterion_ref,
                        session_id=session_ref,
                        count_value=int(row.get("count_value", 0)),
                        is_fulfilled=bool(row.get("is_fulfilled", False))
                    )
                    db.add(uc)
                    db.flush()
            db.commit()

        # Ensure auto-increment sequences continue from the correct ID
        try:
            sequence_resets = [
                ("users", "users_id_seq"),
                ("teams", "teams_id_seq"),
                ("roles", "roles_id_seq"),
                ("criteria", "criteria_id_seq"),
                ("sessions", "sessions_id_seq"),
                ("user_criteria", "user_criteria_id_seq"),
                ("user_criterion_texts", "user_criterion_texts_id_seq"),
                ("user_session_roles", "user_session_roles_id_seq"),
            ]

            for table, seq in sequence_resets:
                db.execute(
                    text(f"SELECT setval('{seq}', (SELECT COALESCE(MAX(id), 0) + 1 FROM {table}), false)")
                )
            db.commit()
        except Exception as seq_err:
            print(f"Warning: Failed to reset sequences — {seq_err}")

        return {"message": "Import completed successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error importing Excel file: {str(e)}")
