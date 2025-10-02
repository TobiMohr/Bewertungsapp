from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import db
from ..models import Phase, PhaseCriterion, Criterion, User, UserCriterion
from ..schemas import PhaseUpdate, PhaseRead

router = APIRouter(prefix="/phases", tags=["phases"])


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


@router.get("/{phase_id}", response_model=PhaseRead)
def get_phase(phase_id: int, db: Session = Depends(get_db)):
    phase = db.query(Phase).options(
        joinedload(Phase.phase_criteria_assoc).joinedload(PhaseCriterion.criterion)
    ).filter(Phase.id == phase_id).first()

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    return phase_to_dict(phase)


@router.put("/{phase_id}", response_model=PhaseRead)
def update_phase(phase_id: int, payload: PhaseUpdate, db: Session = Depends(get_db)):
    phase = db.query(Phase).options(
        joinedload(Phase.phase_criteria_assoc).joinedload(PhaseCriterion.criterion)
    ).filter(Phase.id == phase_id).first()

    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    phase.title = payload.title
    phase.description = payload.description

    # Extract new criteria
    new_criteria = payload.criteria or []

    # Merge criteria (same logic as sessions)
    existing_assoc = {assoc.criterion_id: assoc for assoc in phase.phase_criteria_assoc}
    for crit in new_criteria:
        if crit.id in existing_assoc:
            existing_assoc[crit.id].weight = crit.weight
        else:
            db_crit = db.query(Criterion).filter_by(id=crit.id).first()
            if db_crit:
                assoc = PhaseCriterion(
                    phase_id=phase.id,
                    criterion_id=db_crit.id,
                    weight=crit.weight
                )
                db.add(assoc)

    db.commit()

    # Update UserCriterion
    create_user_criteria_for_phase(db, phase)

    # Reload with relations
    phase = db.query(Phase).options(
        joinedload(Phase.phase_criteria_assoc).joinedload(PhaseCriterion.criterion)
    ).filter(Phase.id == phase_id).first()

    return phase_to_dict(phase)


def phase_to_dict(phase: Phase) -> dict:
    return {
        "id": phase.id,
        "title": phase.title,
        "description": phase.description,
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
