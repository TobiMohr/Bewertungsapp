from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import db
from ..models import Criterion, UserCriterion, User
from ..schemas.criterias import (
    CriterionType,
    CriterionCreate,
    CriterionRead,
    UserCriterionRead,
)

router = APIRouter(prefix="/criteria", tags=["criteria"])


def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# ----- Criterion -----
@router.post("/", response_model=CriterionRead)
def create_criterion(
    payload: CriterionCreate, session: Session = Depends(get_db)
):
    existing = session.query(Criterion).filter(Criterion.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Criterion already exists")

    new_crit = Criterion(name=payload.name, type=payload.type)
    session.add(new_crit)
    session.commit()
    session.refresh(new_crit)
    return new_crit


@router.get("/", response_model=List[CriterionRead])
def list_criteria(session: Session = Depends(get_db)):
    return session.query(Criterion).all()


# ----- UserCriterion -----
@router.post("/{criterion_id}/assign/{user_id}", response_model=UserCriterionRead)
def assign_criterion_to_user(criterion_id: int, user_id: int, session: Session = Depends(get_db)):
    criterion = session.query(Criterion).get(criterion_id)
    user = session.query(User).get(user_id)

    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id)
        session.add(uc)
        session.commit()
        session.refresh(uc)
    return uc


@router.post("/{criterion_id}/increment/{user_id}", response_model=UserCriterionRead)
def increment_user_criterion(criterion_id: int, user_id: int, session: Session = Depends(get_db)):
    criterion = session.query(Criterion).get(criterion_id)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if criterion.type != CriterionType.countable:
        raise HTTPException(status_code=400, detail="Criterion is not countable")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, count_value=0)
        session.add(uc)

    uc.count_value = (uc.count_value or 0) + 1
    session.commit()
    session.refresh(uc)
    return uc


@router.put("/{criterion_id}/set/{user_id}", response_model=UserCriterionRead)
def set_boolean_value(
    criterion_id: int, user_id: int, value: bool, session: Session = Depends(get_db)
):
    criterion = session.query(Criterion).get(criterion_id)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if criterion.type != CriterionType.boolean:
        raise HTTPException(status_code=400, detail="Criterion is not boolean")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id)
        session.add(uc)

    uc.is_fulfilled = value
    session.commit()
    session.refresh(uc)
    return uc
