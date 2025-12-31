# interaction.py
from sqlalchemy import Column, Text, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from .base import BaseModel

class Like(BaseModel):
    __tablename__ = 'likes'
    __table_args__ = (
        UniqueConstraint('user_id', 'post_id', name='unique_like'),
        {'extend_existing': True}
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)


class Comment(BaseModel):
    __tablename__ = 'comments'
    __table_args__ = (
        # uncomment in case you want only one comment per post
        # UniqueConstraint('user_id', 'post_id', name='unique_comment'), 
        {'extend_existing': True}
    )

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False, index=True)
    post_id = Column(UUID(as_uuid=True), ForeignKey('posts.id', ondelete='CASCADE'), nullable=False, index=True)
    content = Column(Text)