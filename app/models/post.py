from sqlalchemy import Column, Text, String, ForeignKey, Integer, Boolean, DateTime, Table
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from models.base import BaseModel
from datetime import datetime, timezone
from db import database

BaseModel.metadata.clear()

post_tags = Table(
    "post_tags",
    BaseModel.metadata,
    Column("post_id", UUID, ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", UUID, ForeignKey("tags.id"), primary_key=True),
)

class UserReference(database.Base):
    __tablename__ = 'user_references'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID, primary_key=True, unique=True)
    username = Column(String(32))
    slug = Column(String(32))
    email = Column(String)
    is_active = Column(Boolean, default=True)
    synced_at = Column(DateTime, default=datetime.now(timezone.utc))

    
class Post(BaseModel):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), index=True, nullable=False)
    file_path = Column(String(255))
    caption = Column(Text)
    views = Column(Integer, default=0)
    
    user = relationship(
        "UserReference",
        primaryjoin="Post.user_id == UserReference.user_id",
        foreign_keys=[user_id],
        viewonly=True  # Read-only, doesn't enforce constraints
    )
    tags = relationship(
        "Tag",
        secondary=post_tags,
        back_populates="posts",
        lazy="selectin",   # good default for API use
    )

class Tag(BaseModel):
    __tablename__ = 'tags'
    __table_args__ = {'extend_existing': True}

    name = Column(String(50), unique=True)

    posts = relationship(
        "Post",
        secondary=post_tags,
        back_populates="tags",
        lazy="selectin",
    )
    