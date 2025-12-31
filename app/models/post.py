from sqlalchemy import Column, Text, String, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import BaseModel

class Post(BaseModel):
    __tablename__ = 'posts'
    __table_args__ = {'extend_existing': True}
    
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    file_path = Column(String(255))
    caption = Column(Text)
    views = Column(Integer, default=0)
    tags = relationship(
        "Tag",
        secondary="post_tags",
        back_populates="posts",
        lazy="selectin",   # good default for API use
    )

class Tag(BaseModel):
    __tablename__ = 'tags'
    __table_args__ = {'extend_existing': True}

    name = Column(String(50), unique=True)

    posts = relationship(
        "Post",
        secondary="post_tags",
        back_populates="tags",
        lazy="selectin",
    )

class PostTag(BaseModel):
    __tablename__ = 'post_tags'
    __table_args__ = {'extend_existing': True}
    
    post_id = Column(UUID, ForeignKey('posts.id'))
    tag_id = Column(UUID, ForeignKey('tags.id'))

