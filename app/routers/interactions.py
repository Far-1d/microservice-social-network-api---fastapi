from fastapi import APIRouter, Depends, HTTPException, Form, status, Path, Query
from db.database import db, Session
from schemas import interaction as schema, post as post_schema
from models import (
    post as models, 
    interaction as iModels
)
from core.oauth import get_current_user
from sqlalchemy import func
import uuid
from typing import List

router = APIRouter(
    prefix='/interactions',
    tags=['post-interactions'],
    dependencies=[]
)

@router.post('/likes')
async def toggle_like(
    post_id:str = Form(...),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id), 
        models.Post.soft_delete == False
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    already_liked = db.query(iModels.Like).filter(
        iModels.Like.post_id == post.id,
        iModels.Like.user_id == uuid.UUID(user_id)
    ).first()

    if already_liked:
        db.delete(already_liked)
        db.commit()
        return { 'value': 0 } # like removed
    
    like = iModels.Like(
        post_id = post.id,
        user_id = uuid.UUID(user_id)
    )
    db.add(like)
    db.commit()
    return { 'value': 1 } # liked


@router.get('/likes', response_model=List[post_schema.PostResponse])
async def list_likes_by_user(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    posts = (
        db.query(models.Post)
        .join(
            iModels.Like, iModels.Like.post_id == models.Post.id, 
        )
        .filter(
            models.Post.soft_delete == False,
            iModels.Like.user_id == uuid.UUID(user_id)
        )
        .order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    like_counts = dict(
        db.query(iModels.Like.post_id, func.count())
        .filter(iModels.Like.post_id.in_([p.id for p in posts]))
        .group_by(iModels.Like.post_id)
        .all()
    )

    comment_counts = dict(
        db.query(iModels.Comment.post_id, func.count())
        .filter(iModels.Comment.post_id.in_([p.id for p in posts]))
        .group_by(iModels.Comment.post_id)
        .all()
    )

    for post in posts:
        post.likes_count = like_counts.get(post.id, 0)
        post.comments_count = comment_counts.get(post.id, 0)

    return posts


@router.post('/comments', response_model=schema.CommentResponse)
async def comment_on_post(
    post_id:str = Form(...),
    comment:str = Form(...),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id), 
        models.Post.soft_delete == False
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    post_comment = iModels.Comment(
        post_id = post.id,
        user_id = uuid.UUID(user_id),
        content = comment
    )
    db.add(post_comment)
    db.commit()
    return post_comment


@router.get('/comments/{post_id}', response_model=List[schema.CommentResponse])
async def list_comments(
    post_id:str = Path(...),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    post = (
        db.query(models.Post)
        .filter(
            models.Post.id == uuid.UUID(post_id),
            models.Post.soft_delete == False,
        )
        .first()
    )
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    comments = (
        db.query(iModels.Comment)
         .filter(
            iModels.Comment.post_id == uuid.UUID(post_id),
            iModels.Comment.soft_delete == False,
         )
         .order_by(iModels.Comment.created_at.desc())
         .offset(offset)
         .limit(limit)
         .all()
    )

    return comments


@router.delete('/comments/{comment_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id:str = Path(...),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    comment = (
        db.query(iModels.Comment)
        .filter(
            iModels.Comment.id == uuid.UUID(comment_id),
            iModels.Comment.soft_delete == False,
        )
        .first()
    )

    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if str(comment.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    comment.soft_delete = True
    db.add(comment)
    db.commit()

    return


@router.post('/bookmarks')
async def toggle_bookmark(
    post_id:str = Form(...),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id), 
        models.Post.soft_delete == False
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    already_marked = db.query(iModels.Bookmark).filter(
        iModels.Bookmark.post_id == post.id,
        iModels.Bookmark.user_id == uuid.UUID(user_id)
    ).first()

    if already_marked:
        db.delete(already_marked)
        db.commit()
        return { 'value': 0 } # bookmark removed
    
    bookmark = iModels.Bookmark(
        post_id = post.id,
        user_id = uuid.UUID(user_id)
    )
    db.add(bookmark)
    db.commit()
    return { 'value': 1 } # bookmarked


@router.get('/bookmarks', response_model=List[post_schema.PostResponse])
async def list_bookmarks_by_user(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    user_id:str = Depends(get_current_user),
    db: Session = Depends(db)
):
    posts = (
        db.query(models.Post)
        .join(
            iModels.Bookmark, iModels.Bookmark.post_id == models.Post.id, 
        )
        .filter(
            models.Post.soft_delete == False,
            iModels.Bookmark.user_id == uuid.UUID(user_id)
        )
        .order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    like_counts = dict(
        db.query(iModels.Like.post_id, func.count())
        .filter(iModels.Like.post_id.in_([p.id for p in posts]))
        .group_by(iModels.Like.post_id)
        .all()
    )

    comment_counts = dict(
        db.query(iModels.Comment.post_id, func.count())
        .filter(iModels.Comment.post_id.in_([p.id for p in posts]))
        .group_by(iModels.Comment.post_id)
        .all()
    )

    for post in posts:
        post.likes_count = like_counts.get(post.id, 0)
        post.comments_count = comment_counts.get(post.id, 0)

    return posts