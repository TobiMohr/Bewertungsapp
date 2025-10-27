from pydantic import BaseModel

class CommentCreateRequest(BaseModel):
    text: str

class CommentResponse(BaseModel):
    id: int
    user_id: int
    session_id: int
    text: str
    created_at: str
    updated_at: str

    class Config:
        orm_mode = True