from fastapi import APIRouter, Depends
from db.database import db, Session
from schemas import post as schema
from models import post as models, interaction as iModels
from core.oauth import get_current_user
from sqlalchemy import desc, func
import uuid

router = APIRouter(
    prefix='/stats',
    tags=['post-stats'],
    dependencies=[]
)


@router.get('/')
async def user_stats(
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    user_uuid = uuid.UUID(user_id)

    # 5 simple, separate queries (cleanest)
    posts_count = db.query(func.count(models.Post.id)).filter(
        models.Post.user_id == user_uuid,
        models.Post.soft_delete == False
    ).scalar()
    
    total_views = db.query(func.coalesce(func.sum(models.Post.views), 0)).filter(
        models.Post.user_id == user_uuid,
        models.Post.soft_delete == False
    ).scalar()
    
    likes = db.query(func.count(iModels.Like.id)).filter(
        iModels.Like.user_id == user_uuid,
        iModels.Like.soft_delete == False
    ).scalar()
    
    comments = db.query(func.count(iModels.Comment.id)).filter(
        iModels.Comment.user_id == user_uuid,
        iModels.Comment.soft_delete == False
    ).scalar()
    
    bookmarks = db.query(func.count(iModels.Bookmark.id)).filter(
        iModels.Bookmark.user_id == user_uuid,
        iModels.Bookmark.soft_delete == False
    ).scalar()

    return {
        "posts": posts_count or 0,
        "views": total_views or 0,
        "likes": likes or 0,
        "comments": comments or 0,
        "bookmarks": bookmarks or 0,
    }