from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import db, models
from ..models import User, UserCriterion, Criterion, SessionCriterion
from ..schemas import SessionCreate, SessionRead, SessionUpdate
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
    # Step 1: Create the session
    new_session = models.Session(
        title=payload.title,
        description=payload.description
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # Step 2: Assign criteria with weight
    if payload.criteria:
        for crit in payload.criteria:
            db_crit = db.query(models.Criterion).filter_by(id=crit.id).first()
            if not db_crit:
                continue
            assoc = SessionCriterion(
                session_id=new_session.id,
                criterion_id=db_crit.id,
                weight=crit.weight
            )
            db.add(assoc)

    db.commit()

    # Step 3: Create UserCriterion entries for all users and all session criteria
    users = db.query(models.User).all()
    for user in users:
        for assoc in new_session.session_criteria_assoc:
            exists = db.query(models.UserCriterion).filter_by(
                user_id=user.id,
                criterion_id=assoc.criterion_id,
                session_id=new_session.id
            ).first()
            if not exists:
                uc = models.UserCriterion(
                    user_id=user.id,
                    criterion_id=assoc.criterion_id,
                    session_id=new_session.id
                )
                db.add(uc)

    db.commit()
    db.refresh(new_session)

    return new_session


@router.get("/", response_model=List[SessionRead])
def get_sessions(session: Session = Depends(get_db)):
    return session.query(models.Session).all()


@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


@router.put("/{session_id}", response_model=SessionRead)
def update_session(session_id: int, session_data: SessionUpdate, db: Session = Depends(get_db)):
    db_session = db.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Update basic fields
    db_session.title = session_data.title
    db_session.description = session_data.description

    if session_data.criteria is not None:
        # Lösche alte Assoziationen
        db.query(SessionCriterion).filter_by(session_id=db_session.id).delete()

        # Füge neue Assoziationen hinzu
        for crit in session_data.criteria:
            db_crit = db.query(models.Criterion).filter_by(id=crit.id).first()
            if not db_crit:
                continue
            assoc = SessionCriterion(
                session_id=db_session.id,
                criterion_id=db_crit.id,
                weight=crit.weight
            )
            db.add(assoc)

        db.commit()

        # UserCriteria aktualisieren (neu erzeugen, falls nötig)
        users = db.query(models.User).all()
        for user in users:
            for crit in session_data.criteria:
                exists = db.query(models.UserCriterion).filter_by(
                    user_id=user.id,
                    criterion_id=crit.id,
                    session_id=db_session.id
                ).first()
                if not exists:
                    uc = models.UserCriterion(
                        user_id=user.id,
                        criterion_id=crit.id,
                        session_id=db_session.id
                    )
                    db.add(uc)

    db.commit()
    db.refresh(db_session)
    return db_session


@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.delete(db_session)
    session.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}
