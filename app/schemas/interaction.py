# schemas/interaction.py
from .base import BaseSchema
# from .user import UserInPost
from typing import Optional
import uuid 


class LikeBase(BaseSchema):
    user_id: uuid.UUID
    post_id: uuid.UUID

class LikeCreate(LikeBase):
    pass

# class LikeResponse(BaseSchema, LikeBase):
#     user: Optional[UserInPost] = None  # Can be included if needed

class CommentBase(BaseSchema):
    content: str

class CommentCreate(CommentBase):
    post_id: uuid.UUID

class CommentUpdate(BaseSchema):
    content: str

class CommentResponse(BaseSchema):
    user_id: uuid.UUID
    post_id: uuid.UUID
    content: str