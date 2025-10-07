from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from typing import List

from .. import db
from ..models import Session as SessionModel, Phase, PhaseCriterion, Criterion, User, UserCriterion
from ..schemas import SessionCreate, SessionRead, SessionUpdate


router = APIRouter(prefix="/sessions", tags=["sessions"])


def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


def create_user_criteria_for_phase(db: Session, phase: Phase):
    users = db.query(User).all()
    for user in users:
        for assoc in phase.phase_criteria_assoc:
            exists = db.query(UserCriterion).filter_by(
                user_id=user.id,
                criterion_id=assoc.criterion_id,
                phase_id=phase.id
            ).first()
            if not exists:
                uc = UserCriterion(
                    user_id=user.id,
                    criterion_id=assoc.criterion_id,
                    phase_id=phase.id
                )
                db.add(uc)
    db.commit()


@router.post("/", response_model=SessionRead)
def create_session(session_data: SessionCreate, db: Session = Depends(get_db)):
    # Create the session
    session = SessionModel(
        title=session_data.title,
        description=session_data.description
    )
    db.add(session)
    db.commit()
    db.refresh(session)

    # Create phases and criteria associations
    for phase_data in session_data.phases:
        phase = Phase(
            title=phase_data.title,
            description=phase_data.description,
            session_id=session.id
        )
        db.add(phase)
        db.commit()
        db.refresh(phase)

        for crit in phase_data.criteria:
            assoc = PhaseCriterion(
                phase_id=phase.id,
                criterion_id=crit.id,
                weight=crit.weight
            )
            db.add(assoc)
        db.commit()

        # Create UserCriterion entries for this phase
        create_user_criteria_for_phase(db, phase)

    # Reload the session with nested phases & criteria
    session = db.query(SessionModel).options(
        joinedload(SessionModel.phases)
        .joinedload(Phase.phase_criteria_assoc)
        .joinedload(PhaseCriterion.criterion)
    ).filter(SessionModel.id == session.id).first()

    return session_to_dict(session)


@router.get("/", response_model=List[SessionRead])
def get_sessions(db: Session = Depends(get_db)):
    sessions = db.query(SessionModel).options(
        joinedload(SessionModel.phases)
        .joinedload(Phase.phase_criteria_assoc)
        .joinedload(PhaseCriterion.criterion)
    ).all()
    return [session_to_dict(s) for s in sessions]


@router.get("/{session_id}", response_model=SessionRead)
def get_session(session_id: int, db: Session = Depends(get_db)):
    db_session = db.query(SessionModel).options(
        joinedload(SessionModel.phases)
        .joinedload(Phase.phase_criteria_assoc)
        .joinedload(PhaseCriterion.criterion)
    ).filter(SessionModel.id == session_id).first()

    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    return session_to_dict(db_session)


@router.put("/{session_id}", response_model=SessionRead)
def update_session(session_id: int, payload: SessionUpdate, db: Session = Depends(get_db)):
    db_session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.title = payload.title
    db_session.description = payload.description

    db.commit()
    db.refresh(db_session)

    # Reload session with phases & criteria for response
    db_session = db.query(SessionModel).options(
        joinedload(SessionModel.phases)
        .joinedload(Phase.phase_criteria_assoc)
        .joinedload(PhaseCriterion.criterion)
    ).filter(SessionModel.id == session_id).first()

    return session_to_dict(db_session)


@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.delete(db_session)
    session.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}

def session_to_dict(session: SessionModel) -> dict:
    return {
        "id": session.id,
        "title": session.title,
        "description": session.description,
        "created_at": session.created_at,
        "updated_at": session.updated_at,
        "phases": [
            {
                "id": phase.id,
                "title": phase.title,
                "description": phase.description,
                "session_id": phase.session_id,
                "created_at": phase.created_at,
                "updated_at": phase.updated_at,
                "criteria": [
                    {
                        "criterion": pc.criterion,
                        "weight": pc.weight
                    }
                    for pc in phase.phase_criteria_assoc
                ]
            }
            for phase in session.phases
        ]
    }

