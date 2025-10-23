from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from .. import db, models, schemas

router = APIRouter(prefix="/teams", tags=["teams"])

# --- DB dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()


# --- Create team ---
@router.post("/", response_model=schemas.TeamRead)
def create_team(team: schemas.TeamCreate, db: Session = Depends(get_db)):
    existing_team = db.query(models.Team).filter(models.Team.name == team.name).first()
    if existing_team:
        raise HTTPException(status_code=400, detail="Team already exists")

    new_team = models.Team(name=team.name)
    db.add(new_team)
    db.commit()
    db.refresh(new_team)
    return new_team


# --- Get all teams ---
@router.get("/", response_model=list[schemas.TeamRead])
def get_teams(db: Session = Depends(get_db)):
    return db.query(models.Team).all()


# --- Get single team with users ---
@router.get("/{team_id}", response_model=schemas.TeamRead)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = (
        db.query(models.Team)
        .options(joinedload(models.Team.users))
        .filter(models.Team.id == team_id)
        .first()
    )
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


# --- Update team name ---
@router.put("/{team_id}", response_model=schemas.TeamRead)
def update_team(team_id: int, updated_team: schemas.TeamCreate, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    team.name = updated_team.name
    db.commit()
    db.refresh(team)
    return team


# --- Delete team ---
@router.delete("/{team_id}", response_model=dict)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    db.delete(team)
    db.commit()
    return {"status": "success", "message": f"Team {team_id} deleted"}


# --- Assign a user to a team ---
@router.put("/{team_id}/assign_user/{user_id}", response_model=schemas.UserRead)
def assign_user_to_team(team_id: int, user_id: int, db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.team_id = team_id
    db.commit()
    db.refresh(user)
    return user
