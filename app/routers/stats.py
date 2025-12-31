from fastapi import APIRouter, Depends, UploadFile, HTTPException, Form, Query, status
from fastapi.responses import FileResponse
from db.database import db, Session
from schemas import post as schema
from models import post as models
from core.oauth import get_current_user, get_optional_user
from dependencies import validate_upload_file
from sqlalchemy import desc
import shutil
import os
import uuid
from typing import Optional, List
import json

router = APIRouter(
    prefix='/stats',
    tags=['post-stats'],
    dependencies=[]
)


@router.get('/{user_id}')
async def user_stats():
    pass

