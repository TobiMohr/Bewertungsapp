from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..models.roles import Role
from ..models.usersessions import UserSessionRole, UserSessionComment
from typing import List
from ..schemas.roles import RoleAssignRequest
from ..schemas.comments import CommentCreateRequest, CommentResponse
from .. import db

router = APIRouter(prefix="/user-sessions", tags=["User Session Roles"])

# --- DB Dependency ---
def get_db():
    db_sess = db.SessionLocal()
    try:
        yield db_sess
    finally:
        db_sess.close()

@router.get("/{session_id}/users/{user_id}/role")
def get_user_role_for_session(session_id: int, user_id: int, db: Session = Depends(get_db)):
    usr_role = db.query(UserSessionRole).filter_by(session_id=session_id, user_id=user_id).first()
    if not usr_role:
        return {"role_id": None, "role_name": None}

    role = db.query(Role).filter_by(id=usr_role.role_id).first()
    return {"role_id": usr_role.role_id, "role_name": role.name if role else None}



@router.post("/{session_id}/users/{user_id}/role")
def assign_role_to_user_in_session(session_id: int, user_id: int, req: RoleAssignRequest, db: Session = Depends(get_db)):
    usr_role = db.query(UserSessionRole).filter_by(session_id=session_id, user_id=user_id).first()
    if usr_role:
        usr_role.role_id = req.role_id
    else:
        usr_role = UserSessionRole(session_id=session_id, user_id=user_id, role_id=req.role_id)
        db.add(usr_role)
    db.commit()
    return {"message": "Role assigned successfully", "role_id": usr_role.role_id}


# Get all comments for a session by a specific user
@router.get("/{session_id}/users/{user_id}/comments", response_model=List[CommentResponse])
def get_comments_for_user_in_session(session_id: int, user_id: int, db: Session = Depends(get_db)):
    comments = (
        db.query(UserSessionComment)
        .filter_by(session_id=session_id, user_id=user_id)
        .order_by(UserSessionComment.created_at.desc())
        .all()
    )
    return comments


# Add a comment for a user in a session
@router.post("/{session_id}/users/{user_id}/comments", response_model=CommentResponse)
def add_comment(session_id: int, user_id: int, req: CommentCreateRequest, db: Session = Depends(get_db)):
    comment = UserSessionComment(
        session_id=session_id,
        user_id=user_id,
        text=req.text
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/{session_id}/users/{user_id}/comments/{comment_id}")
def delete_comment(session_id: int, user_id: int, comment_id: int, db: Session = Depends(get_db)):
    comment = (
        db.query(UserSessionComment)
        .filter_by(id=comment_id, session_id=session_id, user_id=user_id)
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted successfully", "deleted_comment_id": comment_id}
