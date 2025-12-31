from fastapi import APIRouter, Depends, UploadFile, HTTPException, Form, Query, status
from fastapi.responses import FileResponse
from db.database import db, Session
from schemas import post as schema
from models import post as models, interaction as iModels
from core.oauth import get_current_user, get_optional_user
from dependencies import validate_upload_file
from sqlalchemy import desc, func
from sqlalchemy.orm import selectinload
import shutil
import os
import uuid
from typing import Optional, List
import json

router = APIRouter(
    prefix='/posts',
    tags=['posts'],
    dependencies=[]
)


def get_file_path(file: UploadFile, user_id:str):
    user_dir = f"media/posts/{user_id}"
    os.makedirs(user_dir, exist_ok=True)
    
    # Generate unique filename
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"{user_dir}/{unique_filename}"

    return file_path


@router.get('/tags', response_model=List[schema.TagBase])
async def list_posts(db: Session= Depends(db)):
    tags = db.query(models.Tag).all()

    return tags

@router.post('/')
async def create_posts(
    caption:str = Form(...),
    tags:str = Form("[]"),
    file: UploadFile = Depends(validate_upload_file), 
    db: Session = Depends(db),
    user_id: str = Depends(get_current_user)
):
    
    # save file
    file_path = get_file_path(file, user_id)
    try:
        with open(file_path, 'wb') as f:
            shutil.copyfileobj(file.file, f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f'Failed to save file: {e}')
    finally:
        file.file.close()

    try:
        db_post = models.Post(
            user_id=uuid.UUID(user_id),
            file_path=file_path,
            caption=caption,
        )
        db.add(db_post)
        db.flush()  # Get post ID without committing

        # Handle tags
        tags = json.loads(tags)
        if tags:
            for tag_name in tags:
                if not tag_name.strip():
                    continue

                tag = db.query(models.Tag).filter(models.Tag.name == tag_name).first()
                if not tag:
                    tag = models.Tag(name=tag_name)
                    db.add(tag)
                    db.flush()  # Get tag ID without committing
                
                post_tag = models.PostTag(post_id=db_post.id, tag_id=tag.id)
                db.add(post_tag)
        
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        
        # 6. Return response with user info
        # return await get_post_response(db, db_post, user_id)
        return {**db_post.__dict__}

    except Exception as e:
        db.rollback()
        # Clean up file if DB fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(500, f"Failed to create post: {str(e)}")

@router.get('/', response_model = List[schema.PostResponse])
async def list_posts(
    tags: Optional[str] = Query(None, description="Tag names, e.g. ?tags=python&tags=fastapi"),
    user: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user_id: Optional[str] = Depends(get_optional_user),
    db: Session= Depends(db)
):
    q = db.query(models.Post).filter(
        models.Post.soft_delete == False,
    )
    
    if current_user_id:
        q = q.filter(
            models.Post.user_id != uuid.UUID(current_user_id)
        )
    
    if user:
        q = q.filter(models.Post.user_id == uuid.UUID(user))
    
    if tags:
        tags = tags.split(',')
        q = (
            q.join(models.PostTag, models.Post.id == models.PostTag.post_id)
             .join(models.Tag, models.Tag.id == models.PostTag.tag_id)
             .filter(models.Tag.name.in_(tags))
             .distinct()
        )

    post_stmt = (
        q.order_by(models.Post.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    post_ids = [p.id for p in post_stmt.all()]
    
    if not post_ids:
        return []

    posts = (
        db.query(models.Post)
        .options(selectinload(models.Post.tags))
        .filter(models.Post.id.in_(post_ids))
        .order_by(models.Post.created_at.desc())
        .all()
    )
    
    # Get counts in bulk
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
    
    if current_user_id:
        bookmark_counts = dict(
            db.query(iModels.Bookmark.post_id, func.count())
            .filter(
                iModels.Bookmark.post_id.in_([p.id for p in posts]),
                iModels.Bookmark.user_id == uuid.UUID(current_user_id)
            )
            .group_by(iModels.Bookmark.post_id)
            .all()
        )

    # Attach counts to posts
    for post in posts:
        post.likes_count = like_counts.get(post.id, 0)
        post.comments_count = comment_counts.get(post.id, 0)
        if current_user_id:
            post.is_bookmarked = bool(bookmark_counts.get(post.id, 0))

    return posts

@router.get('/{post_id}', response_model = schema.PostResponse)
async def get_post_by_id(
    post_id: str, 
    db: Session= Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id),
        models.Post.soft_delete == False,
    ).order_by(
        models.Post.created_at.desc()
    ).first()

    post.views += 1
    db.add(post)
    db.commit()

    return post

@router.patch('/{post_id}', response_model = schema.PostResponse)
async def update_post(
    post_id: str,
    data: schema.PostUpdate,
    user_id: str = Depends(get_current_user),
    db: Session= Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id),
        models.Post.soft_delete == False
    ).first()

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    
    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")

    update_data = data.model_dump(exclude_unset=True)
    if "caption" in update_data:
        post.caption = update_data["caption"]

    if "tags" in update_data and update_data["tags"] is not None:
        new_tag_names = update_data["tags"]

        # Normalize / dedupe
        new_tag_names = list({name.strip() for name in new_tag_names if name.strip()})

        # Fetch existing Tag objects
        existing_tags = (
            db.query(models.Tag)
            .filter(models.Tag.name.in_(new_tag_names))
            .all()
        )
        existing_by_name = {t.name: t for t in existing_tags}

        # Create tags that don't exist yet
        tags_for_post = []
        for name in new_tag_names:
            tag = existing_by_name.get(name)
            if not tag:
                tag = models.Tag(name=name)
                db.add(tag)
                db.flush()  # assign id
                existing_by_name[name] = tag
            tags_for_post.append(tag)

        # Replace post.tags collection (SQLAlchemy manages PostTag rows)
        post.tags = tags_for_post

    db.add(post)
    db.commit()
    db.refresh(post)
    return post

@router.delete('/{post_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: str,
    user_id: str = Depends(get_current_user),
    db: Session= Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id),
        models.Post.soft_delete == False
    ).first()

    
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if str(post.user_id) != user_id:
        raise HTTPException(status_code=403, detail="Not allowed")
    
    post.soft_delete = True
    db.add(post)
    db.commit()
    
    return

@router.get("/{post_id}/media/")
async def serve_post_media(
    post_id: str, 
    user_id: str = Depends(get_current_user),
    db: Session = Depends(db)
):
    post = db.query(models.Post).filter(
        models.Post.id == uuid.UUID(post_id), 
        models.Post.user_id == uuid.UUID(user_id)
    ).first()
    
    if not post or post.soft_delete:
        raise HTTPException(404, "Post not found")
        
    return FileResponse(
        post.file_path, 
        media_type="image/jpeg",  # or detect from file
        filename=f"post_{post_id}.jpg"
    )
