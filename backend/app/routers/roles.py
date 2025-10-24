from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.sql import exists
from typing import List
from datetime import datetime

from .. import db
from ..models import Role, UserSessionRole, SessionCriterion, Session as SessionModel
from ..schemas.roles import RoleCreate, RoleRead, RoleUpdate

router = APIRouter(prefix="/roles", tags=["roles"])

# --- DB Dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

# --- CREATE Role ---
@router.post("/", response_model=RoleRead)
def create_role(payload: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter_by(name=payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role with this name already exists")
    
    now = datetime.utcnow()
    role = Role(
        name=payload.name,
        description=payload.description,
        created_at=now,
        updated_at=now
    )
    db.add(role)
    db.commit()
    db.refresh(role)
    return role

# --- READ ALL Roles ---
@router.get("/", response_model=List[RoleRead])
def get_roles(db: Session = Depends(get_db)):
    roles = db.query(Role).all()
    result = []
    for role in roles:
        # Check if any session criterion or user role references this role
        has_dependencies = db.query(exists().where(SessionCriterion.role_id == role.id)).scalar() \
                        or db.query(exists().where(UserSessionRole.role_id == role.id)).scalar()
        result.append({
            "id": role.id,
            "name": role.name,
            "description": role.description,
            "has_dependencies": has_dependencies
        })
    return result

# --- READ ONE Role ---
@router.get("/{role_id}", response_model=RoleRead)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).options(
        joinedload(Role.user_sessions).joinedload(UserSessionRole.user),
        joinedload(Role.user_sessions).joinedload(UserSessionRole.session)
    ).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

# --- UPDATE Role ---
@router.put("/{role_id}", response_model=RoleRead)
def update_role(role_id: int, payload: RoleUpdate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    role.name = payload.name
    role.description = payload.description
    db.commit()
    db.refresh(role)
    return role

# --- DELETE Role ---
@router.delete("/{role_id}", response_model=dict)
def delete_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    dependent = db.query(SessionCriterion).filter_by(role_id=role.id).first()
    if dependent:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete role: dependent session criteria exist"
        )
    db.delete(role)
    db.commit()
    return {"status": "success", "message": f"Role {role_id} deleted"}


def get_effective_criterion_weight(
    db: Session, user_id: int, session_id: int, criterion_id: int
) -> int:
    """
    Returns the effective weight of a criterion for a user in a session,
    taking the user's role in that session into account.
    If a role-specific weight exists, it will be returned.
    Otherwise, the default session weight is returned.
    """

    # Step 1: Fetch the user's role in this session (if any)
    user_role = (
        db.query(UserSessionRole)
        .filter_by(user_id=user_id, session_id=session_id)
        .first()
    )
    role_id = user_role.role_id if user_role else None

    # Step 2: Try to find a session criterion with matching role
    weight_entry = (
        db.query(SessionCriterion)
        .filter_by(
            session_id=session_id,
            criterion_id=criterion_id,
            role_id=role_id  # can be None
        )
        .first()
    )

    # Step 3: If role-specific weight exists, return it
    if weight_entry:
        return weight_entry.weight

    # Step 4: Fallback: return default weight without role
    default_entry = (
        db.query(SessionCriterion)
        .filter_by(
            session_id=session_id,
            criterion_id=criterion_id,
            role_id=None
        )
        .first()
    )

    if default_entry:
        return default_entry.weight

    # Step 5: If nothing found, fallback to 1
    return 1
