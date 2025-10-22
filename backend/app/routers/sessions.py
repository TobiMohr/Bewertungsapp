from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import db
from ..models import (
    Session as SessionModel,
    SessionCriterion,
    Criterion,
    User,
    UserCriterion,
    UserSessionRole
)
from ..schemas import SessionCreate, SessionRead, SessionUpdate


router = APIRouter(prefix="/sessions", tags=["sessions"])


# --- DB Dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# --- Helper: create user_criteria entries for a session ---
def create_user_criteria_for_session(db: Session, session: SessionModel):
    """
    Create UserCriterion entries for all users in a session,
    taking into account their role and the weight of each criterion.
    """

    # Step 1: Fetch all users
    users = db.query(User).all()

    # Step 2: Loop through all users
    for user in users:

        # Step 2a: Fetch the user's role in this session (if any)
        user_role = (
            db.query(UserSessionRole)
            .filter_by(user_id=user.id, session_id=session.id)
            .first()
        )
        role_id = user_role.role_id if user_role else None

        # Step 2b: Loop through all session criteria
        for assoc in session.session_criteria_assoc:

            # Step 2c: Determine the effective weight
            # Try role-specific weight first
            weight_entry = (
                db.query(SessionCriterion)
                .filter_by(
                    session_id=session.id,
                    criterion_id=assoc.criterion_id,
                    role_id=role_id
                )
                .first()
            )
            if weight_entry:
                effective_weight = weight_entry.weight
            else:
                # Fallback to default weight (role_id=None)
                default_entry = (
                    db.query(SessionCriterion)
                    .filter_by(
                        session_id=session.id,
                        criterion_id=assoc.criterion_id,
                        role_id=None
                    )
                    .first()
                )
                effective_weight = default_entry.weight if default_entry else 1

            # Step 2d: Check if UserCriterion already exists
            exists = db.query(UserCriterion).filter_by(
                user_id=user.id,
                criterion_id=assoc.criterion_id,
                session_id=session.id
            ).first()

            # Step 2e: Create UserCriterion if it does not exist
            if not exists:
                uc = UserCriterion(
                    user_id=user.id,
                    criterion_id=assoc.criterion_id,
                    session_id=session.id
                )
                # Optional: store weight somewhere if needed in UserCriterion
                # uc.weight = effective_weight
                db.add(uc)

    db.commit()


# --- CREATE ---
@router.post("/", response_model=SessionRead)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    session = SessionModel(
        title=payload.title,
        description=payload.description,
        parent_id=payload.parent_id
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Add criteria if any
    for crit in payload.criteria or []:
        db_crit = db.query(Criterion).filter_by(id=crit.id).first()
        if db_crit:
            assoc = SessionCriterion(
                session_id=session.id,
                criterion_id=db_crit.id,
                role_id=crit.role_id,
                weight=crit.weight
            )
            db.add(assoc)
    db.commit()

    create_user_criteria_for_session(db, session)

    # Reload with relations
    session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == session.id).first()

    return session_to_dict(session)


# --- READ ALL ---
@router.get("/", response_model=List[SessionRead])
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).all()
    return [session_to_dict(s) for s in sessions if s.parent_id is None]


# --- READ ONE ---
@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_to_dict(session)


# --- UPDATE ---
@router.put("/{session_id}", response_model=SessionRead)
def update_session(session_id: int, payload: SessionUpdate, db: Session = Depends(get_db)):
    session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = payload.title
    session.description = payload.description
    session.parent_id = payload.parent_id

    # Update or add criteria
    new_criteria = payload.criteria or []
    existing_assoc = {assoc.criterion_id: assoc for assoc in session.session_criteria_assoc}

    for crit in new_criteria:
        # Check if row with this session_id, criterion_id, role_id exists
        assoc = db.query(SessionCriterion).filter_by(
            session_id=session.id,
            criterion_id=crit.id,
            role_id=crit.role_id
        ).first()
        
        if assoc:
            # Only update the weight
            assoc.weight = crit.weight
        else:
            # Add new row
            db_crit = db.query(Criterion).filter_by(id=crit.id).first()
            if db_crit:
                new_assoc = SessionCriterion(
                    session_id=session.id,
                    criterion_id=db_crit.id,
                    role_id=crit.role_id,
                    weight=crit.weight
                )
                db.add(new_assoc)

    db.commit()
    create_user_criteria_for_session(db, session)

    # Reload updated session
    session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == session.id).first()

    return session_to_dict(session)


# --- DELETE ---
@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, db: Session = Depends(get_db)):
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    db.delete(session)
    db.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}

@router.post("/{session_id}/copy", response_model=SessionRead)
def copy_session(session_id: int, payload: dict, db: Session = Depends(get_db)):
    """
    Duplicate a session (including metadata, criteria, and optionally child sessions).
    """
    session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == session_id).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    new_title = payload.get("title") or f"{session.title} (Copy)"

    # Create new session
    copied_session = SessionModel(
        title=new_title,
        description=session.description,
        parent_id=session.parent_id
    )
    db.add(copied_session)
    db.commit()
    db.refresh(copied_session)

    # Copy criteria
    for assoc in session.session_criteria_assoc:
        new_assoc = SessionCriterion(
            session_id=copied_session.id,
            criterion_id=assoc.criterion_id,
            weight=assoc.weight
        )
        db.add(new_assoc)
    db.commit()

    # Create user criteria for copied session
    create_user_criteria_for_session(db, copied_session)

    # Recursively copy children
    def copy_children(parent_session: SessionModel, new_parent: SessionModel):
        for child in parent_session.children:
            copied_child = SessionModel(
                title=f"{child.title} (Copy)",
                description=child.description,
                parent_id=new_parent.id
            )
            db.add(copied_child)
            db.commit()
            db.refresh(copied_child)

            # Copy criteria
            for assoc in child.session_criteria_assoc:
                new_assoc = SessionCriterion(
                    session_id=copied_child.id,
                    criterion_id=assoc.criterion_id,
                    weight=assoc.weight
                )
                db.add(new_assoc)
            db.commit()

            create_user_criteria_for_session(db, copied_child)

            # Recurse for deeper hierarchy
            copy_children(child, copied_child)

    copy_children(session, copied_session)

    # Reload with relations for return
    copied_session = db.query(SessionModel).options(
        joinedload(SessionModel.session_criteria_assoc).joinedload(SessionCriterion.criterion),
        joinedload(SessionModel.children)
    ).filter(SessionModel.id == copied_session.id).first()

    return session_to_dict(copied_session)



# --- UTIL: Recursive dict serializer ---
def session_to_dict(session: SessionModel) -> dict:
    return {
        "id": session.id,
        "title": session.title,
        "description": session.description,
        "parent_id": session.parent_id,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "criteria": [
            {
                "criterion": sc.criterion,
                "role_id": sc.role_id,
                "weight": sc.weight
            }
            for sc in session.session_criteria_assoc
        ],
        "children": [session_to_dict(child) for child in session.children]
    }
