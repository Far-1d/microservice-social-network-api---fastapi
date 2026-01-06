from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from core.notifications import notifications
from core.oauth import get_current_user

router = APIRouter()

@router.get("/notifications/")
async def stream_notifications(
    user_id: str = Depends(get_current_user)
):
    client_id = f"user_{user_id}"
    
    return StreamingResponse(notifications.generate_message_stream(client_id), media_type="text/event-stream")
