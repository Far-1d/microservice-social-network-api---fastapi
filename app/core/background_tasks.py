from typing import Optional
from fastapi import Depends
from models import post as models
from db.database import SessionLocal  
import uuid
from core.notifications import notifications
from core.communications import request_manager, response_manager

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


async def notify_new_post(post_id: str, author_id:str):
    """Called when someone comments"""
    print('notifying userssss')
    correlation_id = await request_manager.request_data(author_id, 'request-followers')
    if not correlation_id:
        return
    
    follower_ids = await response_manager.wait_for_response(correlation_id, timeout=30)

    if not follower_ids:
        return
    
    await notifications.notify_users(
        follower_ids,
        "new_post",
        {
            "user_id": str(author_id),
            "post_id": post_id,
            "type": "post"
        }
    )

# To Do: cache likes to prevent repeating notifications
async def notify_post_liked(post_id: str, liker_id: str, author_id: str):
    """Called when someone likes a post"""
    if str(author_id) != liker_id:  # Don't notify self
        await notifications.notify_user(
            str(author_id),
            "post_liked",
            {
                "post_id": post_id,
                "liker_id": liker_id,
                "type": "like"
            }
        )

# To Do: cache comments to prevent repeating notifications
async def notify_new_comment(post_id: str, commenter_id: str, author_id: str, comment: str):
    """Called when someone comments"""
    if str(author_id) != commenter_id:
        await notifications.notify_user(
            str(author_id),
            "new_comment",
            {
                "post_id": post_id,
                "commenter_id": commenter_id,
                "type": "comment",
                "comment": comment
            }
        )