# schemas/filters.py
from pydantic import BaseModel
from typing import Optional
import uuid

class PostFilters(BaseModel):
    user_id: Optional[uuid.UUID] = None
    tag: Optional[str] = None
    search: Optional[str] = None  # Search in caption
    min_views: Optional[int] = None
    limit: int = 20
    offset: int = 0

class FeedFilters(BaseModel):
    """For user's feed (followed users)"""
    limit: int = 20
    offset: int = 0

class CommentFilters(BaseModel):
    post_id: uuid.UUID
    limit: int = 50
    offset: int = 0