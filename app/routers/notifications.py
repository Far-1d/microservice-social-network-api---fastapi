from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from core.notifications import notifications
from core.oauth import get_current_user
import json
import asyncio

router = APIRouter()

@router.get("/notifications/")
async def stream_notifications(
    user_id: str = Depends(get_current_user)
):
    async def event_stream():
        queue = asyncio.Queue()
        
        async def callback(event: dict):
            await queue.put(event)
        
        client_id = f"user_{user_id}"
        
        # Subscribe client
        await notifications.subscribe(client_id, callback)
        
        try:
            while True:
                event = await asyncio.wait_for(queue.get(), timeout=30.0)
                yield f"data: {json.dumps(event)}\n\n"
        except asyncio.TimeoutError:
            yield ": heartbeat\n\n"
        except asyncio.CancelledError:
            pass
        finally:
            await notifications.unsubscribe(client_id)
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")
