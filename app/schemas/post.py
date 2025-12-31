from .base import BaseSchema, BaseModel
from pydantic import Field
from .user import UserInPost
from typing import Optional, List
from datetime import datetime
import uuid


class TagBase(BaseSchema):
    name: str


class PostBase(BaseSchema):
    caption: Optional[str] = None
    tags: List[str] = []  # List of tag names

class PostCreate(PostBase):
    """For creating a post"""
    pass

class PostUpdate(BaseModel):
    """For updating a post"""
    caption: Optional[str] = None
    tags: Optional[List[str]] = Field(default=None)

class PostInDB(BaseSchema):
    """Database representation"""
    user_id: uuid.UUID
    caption: Optional[str]
    views: int = 0

class PostResponse(PostInDB):
    """Full response with relationships"""
    # user: UserInPost  # Will fetch from Django API
    tags: List[TagBase] = []
    likes_count: int = 0
    comments_count: int = 0
    is_liked: bool = False
    is_bookmarked: bool = False
    updated_at: datetime
    # Optional: include first few comments