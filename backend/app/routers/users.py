from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import db, schemas, security, models

router = APIRouter(prefix="/users", tags=["users"])

# --- DB dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# --- Create user ---
@router.post("/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create new user
    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=security.hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Initialize user criteria for all sessions and subsessions
    sessions = db.query(models.Session).filter(models.Session.parent_id == None).all()
    def create_user_criteria_for_all_sessions(sessions):
        for sess in sessions:
            for crit in sess.criteria:
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
            if sess.children:
                create_user_criteria_for_all_sessions(sess.children)

    create_user_criteria_for_all_sessions(sessions)
    db.commit()

    return new_user


# --- Get all users ---
@router.get("/", response_model=list[schemas.UserRead])
def get_users(session: Session = Depends(get_db)):
    return session.query(models.User).all()


# --- Get single user ---
@router.get("/{user_id}", response_model=schemas.UserRead)
def get_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


# --- Get user evaluation ---
@router.get("/{user_id}/evaluation")
def get_user_evaluation(user_id: int, db: Session = Depends(get_db)):
    sessions = (
        db.query(models.Session)
        .options(
            joinedload(models.Session.children),
            joinedload(models.Session.criteria),
            joinedload(models.Session.user_criteria).joinedload(models.UserCriterion.criterion)
        )
        .filter(models.Session.parent_id == None)  # top-level sessions
        .all()
    )

    def user_session_dict(session: models.Session):
        return {
            "id": session.id,
            "title": session.title,
            "description": session.description,
            "userCriteria": [
                {
                    "id": uc.id,
                    "count_value": uc.count_value,
                    "is_fulfilled": uc.is_fulfilled,
                    "text_value": uc.text_values,
                    "criterion": {
                        "id": uc.criterion.id,
                        "name": uc.criterion.name,
                        "type": uc.criterion.type.value,
                        "role_weights": [
                            {
                                "role_id": assoc.role_id,
                                "weight": assoc.weight
                            }
                            for assoc in session.session_criteria_assoc
                            if assoc.criterion_id == uc.criterion.id
                        ],
                    },
                }
                for uc in session.user_criteria
                if uc.user_id == user_id
            ],
            "children": [user_session_dict(child) for child in session.children]
        }

    return [user_session_dict(sess) for sess in sessions]


# --- Update user ---
@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, updated_user: schemas.UserUpdate, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    user.email = updated_user.email
    
    session.commit()
    session.refresh(user)
    return user


# --- Delete user ---
@router.delete("/{user_id}", response_model=dict)
def delete_user(user_id: int, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(user)
    session.commit()
    return {"status": "success", "message": f"User {user_id} deleted"}
