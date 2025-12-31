from fastapi import Depends
from models import post as models
from db.database import SessionLocal  
import uuid

async def increment_views( post_id: str ):
    db = SessionLocal()

    try:
        post = db.query(models.Post).filter(
            models.Post.id == uuid.UUID(post_id),
            models.Post.soft_delete == False,
        ).first()

        if post:
            post.views += 1
            db.commit()

    finally:
        db.close()