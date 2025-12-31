# schemas/user.py
from .base import BaseSchema
from typing import Optional

class UserBase(BaseSchema):
    username: str
    # Add other fields you need from Django

class UserInPost(UserBase):
    """Minimal user info for embedding in posts"""
    profile_pic: Optional[str] = None