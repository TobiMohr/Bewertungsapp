from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import db, schemas, security, models


router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

@router.post("/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 🔹 Check if user exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # 🔹 Create new user
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=security.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # 🔹 Create UserCriterion entries for all existing sessions & their criteria
    sessions = db.query(models.Session).all()
    for sess in sessions:
        for crit in sess.criteria:  # alle Kriterien der Session
            exists = db.query(models.UserCriterion).filter_by(
                user_id=new_user.id,
                criterion_id=crit.id,
                session_id=sess.id
            ).first()
            if not exists:
                uc = models.UserCriterion(
                    user_id=new_user.id,
                    criterion_id=crit.id,
                    session_id=sess.id
                )
                db.add(uc)

    db.commit()

    return new_user

@router.get("/", response_model=list[schemas.UserRead])
def get_users(session: Session = Depends(get_db)):
    return session.query(models.User).all()

# Get a single user by ID
@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.get("/{user_id}/evaluation")
def get_user_evaluation(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.Session)
        .options(
            joinedload(models.Session.phases)
            .joinedload(models.Phase.phase_criteria_assoc)
            .joinedload(models.PhaseCriterion.criterion), 
            joinedload(models.Session.phases)
            .joinedload(models.Phase.user_criteria)
            .joinedload(models.UserCriterion.criterion)
        )
        .all()
    )

    return [
        {
            "id": s.id,
            "title": s.title,
            "description": s.description,
            "phases": [
                {
                    "id": p.id,
                    "title": p.title,
                    "description": p.description,
                    "userCriteria": [
                        {
                            "id": uc.id,
                            "count_value": uc.count_value,
                            "is_fulfilled": uc.is_fulfilled,
                            "text_value": uc.text_value,
                            "criterion": {
                                "id": uc.criterion.id,
                                "name": uc.criterion.name,
                                "type": uc.criterion.type.value,
                                "weight": next(
                                    (
                                        assoc.weight
                                        for assoc in p.phase_criteria_assoc
                                        if assoc.criterion_id == uc.criterion.id
                                    ),
                                    None,
                                ),
                            },
                        }
                        for uc in p.user_criteria
                        if uc.user_id == user_id
                    ],
                }
                for p in s.phases
            ],
        }
        for s in sessions
    ]


# Update a user by ID
@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, updated_user: schemas.UserUpdate, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    user.email = updated_user.email
    
    session.commit()
    session.refresh(user)
    return user

@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"status": "success", "message": f"User {user_id} deleted"}

