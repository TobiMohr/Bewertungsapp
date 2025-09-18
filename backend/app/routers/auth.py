from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from .. import db, models, schemas, security

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=schemas.UserRead)
def register_user(user: schemas.UserCreate, session: Session = Depends(db.get_db)):
    existing_user = session.query(models.User).filter(models.User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
        email=user.email,
        password_hash=security.hash_password(user.password)
    )
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return new_user

@router.post("/login", response_model=schemas.UserRead)
def login_user(user: schemas.UserLogin, session: Session = Depends(db.get_db)):
    db_user = session.query(models.User).filter(models.User.email == user.email).first()
    if not db_user or not security.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return db_user
