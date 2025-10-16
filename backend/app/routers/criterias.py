from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from enum import Enum
from .. import db
from ..models import Criterion, User, UserCriterion, Phase
from ..schemas.criterias import (
    CriterionType,
    CriterionCreate,
    CriterionRead,
    UserCriterionUpdate,
    UserCriterionRead,
)
import logging

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/criteria", tags=["criteria"])

# ----- Database Dependency -----
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

# ----- Helper Functions -----
def get_or_404(session: Session, model, id: int, name: str):
    obj = session.query(model).get(id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return obj

def get_or_create_usercriterion(session: Session, user_id: int, criterion_id: int, phase_id: int):
    uc = (
        session.query(UserCriterion)
        .filter_by(user_id=user_id, criterion_id=criterion_id, phase_id=phase_id)
        .first()
    )
    if not uc:
        uc = UserCriterion(user_id=user_id, criterion_id=criterion_id, phase_id=phase_id)
        session.add(uc)
        session.commit()
        session.refresh(uc)
    return uc

def get_user_criteria_recursive(phase: Phase, user_id: int, session: Session) -> List[UserCriterion]:
    data = session.query(UserCriterion).filter_by(user_id=user_id, phase_id=phase.id).all()
    for child in phase.children:
        data.extend(get_user_criteria_recursive(child, user_id, session))
    return data

# ----- Criterion -----
@router.post("/", response_model=CriterionRead)
def create_criterion(payload: CriterionCreate, session: Session = Depends(get_db)):
    existing = session.query(Criterion).filter(Criterion.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Criterion already exists")

    new_crit = Criterion(
        name=payload.name,
        type=CriterionType(payload.type)
    )
    session.add(new_crit)
    session.commit()
    session.refresh(new_crit)
    return new_crit

@router.get("/", response_model=List[CriterionRead])
def list_criteria(session: Session = Depends(get_db)):
    return session.query(Criterion).all()

# ----- UserCriterion -----
@router.get("/user/{user_id}/phase/{phase_id}", response_model=List[UserCriterionRead])
def get_user_criteria(user_id: int, phase_id: int, session: Session = Depends(get_db)):
    phase = (
        session.query(Phase)
        .options(joinedload(Phase.children))
        .filter(Phase.id == phase_id)
        .first()
    )
    if not phase:
        raise HTTPException(status_code=404, detail="Phase not found")

    data = get_user_criteria_recursive(phase, user_id, session)
    for uc in data:
        _ = uc.criterion  # preload relationship
    return data

# ----- Unified Update Endpoint -----
class UpdateAction(str, Enum):
    increment = "increment"
    decrement = "decrement"
    set_boolean = "set_boolean"
    set_text = "set_text"

@router.put("/{criterion_id}/{user_id}/phase/{phase_id}", response_model=UserCriterionRead)
def update_user_criterion(
    criterion_id: int,
    user_id: int,
    phase_id: int,
    action: UpdateAction = Query(...),
    payload: Optional[UserCriterionUpdate] = Body(None),
    session: Session = Depends(get_db)
):
    criterion = get_or_404(session, Criterion, criterion_id, "Criterion")
    phase = get_or_404(session, Phase, phase_id, "Phase")
    uc = get_or_create_usercriterion(session, user_id, criterion_id, phase_id)

    value = payload.value if payload else None

    if action == UpdateAction.increment:
        uc.count_value = (uc.count_value or 0) + 1
    elif action == UpdateAction.decrement:
        uc.count_value = max((uc.count_value or 0) - 1, 0)
    elif action == UpdateAction.set_boolean:
        uc.is_fulfilled = bool(value)
    elif action == UpdateAction.set_text:
        uc.text_value = str(value)

    session.commit()
    session.refresh(uc)
    return uc

# ----- List all UserCriterion -----
@router.get("/usercriteria", response_model=List[UserCriterionRead])
def list_all_user_criteria(session: Session = Depends(get_db)):
    data = session.query(UserCriterion).all()
    for uc in data:
        _ = uc.criterion 
    return data

# ----- Get UserCriterion for a Criterion -----
@router.get("/{criterion_id}/users", response_model=List[UserCriterionRead])
def get_user_criteria_for_criterion(
    criterion_id: int, phase_id: Optional[int] = None, session: Session = Depends(get_db)
):
    query = session.query(UserCriterion).join(User).filter(UserCriterion.criterion_id == criterion_id)
    if phase_id:
        query = query.filter(UserCriterion.phase_id == phase_id)
    
    results = query.all()
    for uc in results:
        _ = uc.user  # preload user relationship
    return results
