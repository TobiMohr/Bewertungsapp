from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import db, models
from ..models import User, UserCriterion, Criterion
from ..schemas import SessionCreate, SessionRead, SessionUpdate, SessionBase
from typing import List

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


@router.post("/", response_model=SessionRead)
def create_session(payload: SessionCreate, db: Session = Depends(get_db)):
    # 🔹 Step 1: Create the session
    new_session = models.Session(
        title=payload.title,
        description=payload.description
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 🔹 Step 2: Assign selected criteria (Many-to-Many)
    if payload.criteria_ids:
        criteria = db.query(models.Criterion).filter(
            models.Criterion.id.in_(payload.criteria_ids)
        ).all()
        new_session.criteria = criteria
        db.commit()

    # 🔹 Step 3: Create UserCriterion entries for all users and all session criteria
    users = db.query(models.User).all()
    for user in users:
        for crit in new_session.criteria:
            exists = db.query(models.UserCriterion).filter_by(
                user_id=user.id,
                criterion_id=crit.id,
                session_id=new_session.id
            ).first()
            if not exists:
                uc = models.UserCriterion(
                    user_id=user.id,
                    criterion_id=crit.id,
                    session_id=new_session.id
                )
                db.add(uc)

    db.commit()

    # 🔹 Step 4: Return the session
    return new_session


# Get all sessions
@router.get("/", response_model=list[SessionRead])
def get_sessions(session: Session = Depends(get_db)):
    return session.query(models.Session).all()


# Get a single session by ID
@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


# Update a session
@router.put("/{session_id}", response_model=SessionRead)
def update_session(session_id: int, session_data: SessionUpdate, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.title = session_data.title
    db_session.description = session_data.description

    session.commit()
    session.refresh(db_session)
    return db_session


# Delete a session
@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.delete(db_session)
    session.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}
