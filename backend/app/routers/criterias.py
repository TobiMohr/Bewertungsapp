from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session
from typing import List

from .. import db
from ..models import Criterion, User, UserCriterion, Session as DbSession
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
def create_criterion(payload: CriterionCreate, session: Session = Depends(get_db)):
    # Check if it already exists
    existing = session.query(Criterion).filter(Criterion.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Criterion already exists")

    # Create the new criterion
    new_crit = Criterion(
        name=payload.name,
        type=CriterionType(payload.type)  # converts string -> Enum
    )
    session.add(new_crit)
    session.commit()
    session.refresh(new_crit)

    # 🔹 Assign it to every user for every session
    users = session.query(User).all()
    sessions = session.query(DbSession).all()
    for user in users:
        for db_sess in sessions:
            exists = session.query(UserCriterion).filter_by(
                user_id=user.id,
                criterion_id=new_crit.id,
                session_id=db_sess.id
            ).first()
            if not exists:
                uc = UserCriterion(user_id=user.id, criterion_id=new_crit.id, session_id=db_sess.id)
                session.add(uc)

    session.commit()

    return new_crit


@router.get("/", response_model=List[CriterionRead])
def list_criteria(session: Session = Depends(get_db)):
    return session.query(Criterion).all()


# ----- UserCriterion -----
@router.get("/user/{user_id}/session/{session_id}", response_model=List[UserCriterionRead])
def get_user_criteria(user_id: int, session_id: int, session: Session = Depends(get_db)):
    # Ensure session exists
    if not session.query(DbSession).get(session_id):
        raise HTTPException(status_code=404, detail="Session not found")

    data = (
        session.query(UserCriterion)
        .filter(UserCriterion.user_id == user_id, UserCriterion.session_id == session_id)
        .all()
    )
    for uc in data:
        _ = uc.criterion
    return data


@router.post("/{criterion_id}/assign/{user_id}/session/{session_id}", response_model=UserCriterionRead)
def assign_criterion_to_user(criterion_id: int, user_id: int, session_id: int, session: Session = Depends(get_db)):
    criterion = session.query(Criterion).get(criterion_id)
    user = session.query(User).get(user_id)
    db_session = session.query(DbSession).get(session_id)

    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        session.add(uc)
        session.commit()
        session.refresh(uc)
    return uc


@router.post("/{criterion_id}/increment/{user_id}/session/{session_id}", response_model=UserCriterionRead)
def increment_user_criterion(criterion_id: int, user_id: int, session_id: int, session: Session = Depends(get_db)):
    criterion = session.query(Criterion).get(criterion_id)
    db_session = session.query(DbSession).get(session_id)

    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if criterion.type.value != "countable":
        raise HTTPException(status_code=400, detail=f"Criterion is not countable, it is '{criterion.type.value}'")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, session_id=session_id, count_value=0)
        session.add(uc)

    uc.count_value = (uc.count_value or 0) + 1
    session.commit()
    session.refresh(uc)
    return uc


@router.put("/{criterion_id}/set/{user_id}/session/{session_id}", response_model=UserCriterionRead)
def set_boolean_value(
    criterion_id: int,
    user_id: int,
    session_id: int,
    value: bool = Query(..., description="Boolean value to set"),
    session: Session = Depends(get_db)
):
    criterion = session.query(Criterion).get(criterion_id)
    db_session = session.query(DbSession).get(session_id)

    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if criterion.type.value != "boolean":
        raise HTTPException(status_code=400, detail=f"Criterion is not boolean, it is '{criterion.type.value}'")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        session.add(uc)

    uc.is_fulfilled = value
    session.commit()
    session.refresh(uc)
    return uc

@router.put("/{criterion_id}/text/{user_id}/session/{session_id}", response_model=UserCriterionRead)
def set_text_value(
    criterion_id: int,
    user_id: int,
    session_id: int,
    value: str = Body(..., embed=True, description="Text for this criterion"),
    session: Session = Depends(get_db)
):
    criterion = session.query(Criterion).get(criterion_id)
    db_session = session.query(DbSession).get(session_id)

    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    if criterion.type.value != "text":
        raise HTTPException(status_code=400, detail=f"Criterion is not type: text, it is type:'{criterion.type.value}'")

    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, session_id=session_id)
        session.add(uc)

    uc.text_value = value
    session.commit()
    session.refresh(uc)
    return uc

# ----- List all UserCriterion -----
@router.get("/usercriteria", response_model=List[UserCriterionRead])
def list_all_user_criteria(session: Session = Depends(get_db)):
    data = session.query(UserCriterion).all()
    for uc in data:
        _ = uc.criterion  # ensure criterion relationship is loaded
    return data

