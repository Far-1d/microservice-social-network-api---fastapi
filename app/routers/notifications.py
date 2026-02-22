from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from app.core.notifications import notifications
from app.core.oauth import get_current_user
from collections import defaultdict

router = APIRouter()


# Track connections per user
user_connections = defaultdict(int)
MAX_CONNECTIONS_PER_USER = 5

@router.get("/notifications/")
async def stream_notifications(
    user_id: str = Depends(get_current_user)
):
    if user_connections[user_id] >= MAX_CONNECTIONS_PER_USER:
        raise HTTPException(429, "Too many open connections")
    
    user_connections[user_id] += 1
    
    async def wrapped_stream():
        try:
            async for message in notifications.generate_message_stream(f"user_{user_id}"):
                yield message
        finally:
            user_connections[user_id] -= 1
    
    return StreamingResponse(wrapped_stream(), media_type="text/event-stream")