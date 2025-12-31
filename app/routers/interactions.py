from fastapi import APIRouter, Depends, HTTPException, Form, status
from db.database import db, Session
from schemas import interaction as schema
from models import (
    post as models, 
    interaction as iModels
)
from core.oauth import get_current_user, get_optional_user
from dependencies import validate_upload_file
from sqlalchemy import desc
import shutil
import os
import uuid
from typing import Optional, List
import json

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

@router.get('/comments')
async def list_comments():
    pass


@router.delete('/comments/{comment_id}')
async def delete_comment():
    pass