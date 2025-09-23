from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import db, models, schemas

router = APIRouter(prefix="/sessions", tags=["sessions"])

def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# Create a new session
@router.post("/", response_model=schemas.SessionRead)
def create_session(session_data: schemas.SessionCreate, session: Session = Depends(get_db)):
    new_session = models.Session(
        title=session_data.title,
        description=session_data.description
    )
    session.add(new_session)
    session.commit()
    session.refresh(new_session)
    return new_session


# Get all sessions
@router.get("/", response_model=list[schemas.SessionRead])
def get_sessions(session: Session = Depends(get_db)):
    return session.query(models.Session).all()


# Get a single session by ID
@router.get("/{session_id}", response_model=schemas.SessionRead)
def get_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session


# Update a session
@router.put("/{session_id}", response_model=schemas.SessionRead)
def update_session(session_id: int, session_data: schemas.SessionUpdate, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    db_session.title = session_data.title
    db_session.description = session_data.description

    session.commit()
    session.refresh(db_session)
    return db_session


# Delete a session
@router.delete("/{session_id}", response_model=dict)
def delete_session(session_id: int, session: Session = Depends(get_db)):
    db_session = session.query(models.Session).filter(models.Session.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.delete(db_session)
    session.commit()
    return {"status": "success", "message": f"Session {session_id} deleted"}
