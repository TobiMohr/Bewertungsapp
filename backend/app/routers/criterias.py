from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from enum import Enum
from .. import db
from ..models import Criterion, User, UserCriterion, UserCriterionText, Session as SessionModel
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
    obj = session.get(model, id)
    if not obj:
        raise HTTPException(status_code=404, detail=f"{name} not found")
    return obj

def get_or_create_usercriterion(session: Session, user_id: int, criterion_id: int, session_id: int):
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
    criteria = session.query(Criterion).all()
    result = []
    for crit in criteria:
        # Check if there are any UserCriterion entries for this criterion
        has_deps = session.query(UserCriterion).filter_by(criterion_id=crit.id).first() is not None

        result.append({
            "id": crit.id,
            "name": crit.name,
            "type": crit.type,
            "created_at": crit.created_at,
            "updated_at": crit.updated_at,
            "has_dependencies": has_deps
        })
    return result

# ----- UserCriterion -----
@router.get("/user/{user_id}/session/{session_id}", response_model=List[UserCriterionRead])
def get_user_criteria(user_id: int, session_id: int, session: Session = Depends(get_db)):
    # Ensure session exists
    db_session = session.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    data = (
        session.query(UserCriterion)
        .options(joinedload(UserCriterion.criterion), joinedload(UserCriterion.text_values))
        .filter_by(user_id=user_id, session_id=session_id)
        .all()
    )   

    for uc in data:
        uc.last_texts = [t.text_value for t in sorted(uc.text_values, key=lambda x: x.created_at, reverse=True) if not t.is_active][:5]

    return data

# ----- Unified Update Endpoint -----
class UpdateAction(str, Enum):
    increment = "increment"
    decrement = "decrement"
    set_boolean = "set_boolean"
    set_text = "set_text"

@router.put("/{criterion_id}/{user_id}/session/{session_id}", response_model=UserCriterionRead)
def update_user_criterion(
    criterion_id: int,
    user_id: int,
    session_id: int,
    action: UpdateAction = Query(...),
    payload: Optional[UserCriterionUpdate] = Body(None),
    session: Session = Depends(get_db)
):
    criterion = get_or_404(session, Criterion, criterion_id, "Criterion")
    db_session = get_or_404(session, SessionModel, session_id, "Session")
    uc = get_or_create_usercriterion(session, user_id, criterion_id, session_id)

    value = getattr(payload, "value", None)

    if action == UpdateAction.increment:
        uc.count_value = (uc.count_value or 0) + 1
    elif action == UpdateAction.decrement:
        uc.count_value = max((uc.count_value or 0) - 1, 0)
    elif action == UpdateAction.set_boolean:
        uc.is_fulfilled = bool(value)
    elif action == UpdateAction.set_text:
        if not value or not isinstance(value, str):
            raise HTTPException(status_code=400, detail="Text value must be provided")
        # Deactivate previous text entries
        for t in uc.text_values:
            t.is_active = False
        # Add new active text
        new_text = UserCriterionText(user_criterion_id=uc.id, text_value=value, is_active=True)
        session.add(new_text)

    session.commit()
    session.refresh(uc)
    return uc

# ----- List all UserCriterion -----
@router.get("/usercriteria", response_model=List[UserCriterionRead])
def list_all_user_criteria(session: Session = Depends(get_db)):
    data = session.query(UserCriterion).options(joinedload(UserCriterion.criterion), joinedload(UserCriterion.text_values)).all()
    for uc in data:
        uc.active_text = next((t.text_value for t in uc.text_values if t.is_active), None)
        uc.last_texts = [t.text_value for t in sorted(uc.text_values, key=lambda x: x.created_at, reverse=True) if not t.is_active][:5]
    return data

# ----- Get UserCriterion for a Criterion -----
@router.get("/{criterion_id}/users", response_model=List[UserCriterionRead])
def get_user_criteria_for_criterion(
    criterion_id: int, session_id: Optional[int] = None, session: Session = Depends(get_db)
):
    query = session.query(UserCriterion).join(User).filter(UserCriterion.criterion_id == criterion_id)
    if session_id:
        query = query.filter(UserCriterion.session_id == session_id)
    
    results = query.all()
    for uc in results:
        _ = uc.user  # preload user relationship
        uc.last_texts = [t.text_value for t in sorted(uc.text_values, key=lambda x: x.created_at, reverse=True) if not t.is_active][:5]
    return results

@router.delete("/{criterion_id}")
def delete_criterion(criterion_id: int, session: Session = Depends(get_db)):
    crit = session.get(Criterion, criterion_id)
    if not crit:
        raise HTTPException(status_code=404, detail="Criterion not found")
    
    # Optional: check if criterion is used in any UserCriterion
    in_use = session.query(UserCriterion).filter_by(criterion_id=criterion_id).first()
    if in_use:
        raise HTTPException(status_code=400, detail="Cannot delete criterion: it is in use")
    
    session.delete(crit)
    session.commit()
    return {"detail": "Criterion deleted"}