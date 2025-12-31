from fastapi import Depends, HTTPException, UploadFile
from typing import Tuple
import os


async def validate_upload_file(
    file: UploadFile,
    max_size_mb: int = 10,
    allowed_types: Tuple[str, ...] = ("image/", "video/")
) -> UploadFile:
    """Dependency to validate uploaded files"""
    
    # Check file size
    if file.size > max_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=400, 
            detail=f"File size exceeds {max_size_mb}MB limit"
        )
    
    # Check file type
    if not any(file.content_type.startswith(t) for t in allowed_types):
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(allowed_types)}"
        )
    
    # Check filename
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")
    
    # Check for empty file
    if file.size == 0:
        raise HTTPException(status_code=400, detail="File is empty")
    
    return file

# Specialized versions for common use cases
async def validate_image_file(
    file: UploadFile = Depends(validate_upload_file),
    allowed_extensions: Tuple[str, ...] = (".jpg", ".jpeg", ".png", ".gif")
) -> UploadFile:
    """Specifically for images only"""
    
    file_ext = os.path.splitext(file.filename)[1].lower()
    
    if file_ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File extension not allowed. Allowed: {', '.join(allowed_extensions)}"
        )
    
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files allowed")
    return file


async def validate_video_file(
    file: UploadFile = Depends(validate_upload_file)
) -> UploadFile:
    """Specifically for videos only"""
    if not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Only video files allowed")
    return file