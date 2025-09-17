from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import db, models, schemas

router = APIRouter(prefix="/users", tags=["users"])
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import db, models, schemas

router = APIRouter(prefix="/users", tags=["users"])

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

@router.post("/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, session: Session = Depends(get_db)):    
    db_user = models.User(
        first_name=user.first_name,
        last_name=user.last_name,
    )
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.get("/", response_model=list[schemas.UserRead])
def get_users(session: Session = Depends(get_db)):
    return session.query(models.User).all()

# Update a user by ID
@router.put("/{user_id}", response_model=schemas.UserRead)
def update_user(user_id: int, updated_user: schemas.UserCreate, session: Session = Depends(get_db)):
    user = session.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Update fields
    user.first_name = updated_user.first_name
    user.last_name = updated_user.last_name
    
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

