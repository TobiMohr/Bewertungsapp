from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..models.roles import UserSessionRole, Role
from ..schemas.roles import RoleAssignRequest
from .. import db

router = APIRouter(prefix="/user-sessions", tags=["User Session Roles"])

# --- DB Dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

@router.get("/{session_id}/users/{user_id}/role")
def get_user_role_for_session(session_id: int, user_id: int, db: Session = Depends(get_db)):
    usr_role = db.query(UserSessionRole).filter_by(session_id=session_id, user_id=user_id).first()
    if not usr_role:
        return {"role_id": None, "role_name": None}

    role = db.query(Role).filter_by(id=usr_role.role_id).first()
    return {"role_id": usr_role.role_id, "role_name": role.name if role else None}



@router.post("/{session_id}/users/{user_id}/role")
def assign_role_to_user_in_session(session_id: int, user_id: int, req: RoleAssignRequest, db: Session = Depends(get_db)):
    usr_role = db.query(UserSessionRole).filter_by(session_id=session_id, user_id=user_id).first()
    if usr_role:
        usr_role.role_id = req.role_id
    else:
        usr_role = UserSessionRole(session_id=session_id, user_id=user_id, role_id=req.role_id)
        db.add(usr_role)
    db.commit()
    return {"message": "Role assigned successfully", "role_id": usr_role.role_id}
