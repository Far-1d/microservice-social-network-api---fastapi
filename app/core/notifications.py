from typing import Dict, List, Callable
from collections import defaultdict
import asyncio
from typing import Iterable

class NotificationManager:
    def __init__(self):
        self.clients: Dict[str, List[Callable]] = defaultdict(list)
    
    async def subscribe(self, client_id: str, callback: Callable):
        self.clients[client_id].append(callback)
    
    async def unsubscribe(self, client_id: str):
        self.clients.pop(client_id, None)
    
    async def publish(self, event_type: str, data: dict):
        # Notify all clients
        for client_id, callbacks in list(self.clients.items()):
            for callback in callbacks:
                try:
                    await callback({
                        "type": event_type,
                        "data": data
                    })
                except:
                    pass  # Client disconnected
    
    async def notify_user(self, user_id: str, event_type: str, data: dict):
        # Filter by user_id if needed
        await self.publish(event_type, {"user_id": user_id, **data})

    async def notify_users(self, user_ids: Iterable[str], event_type: str, data: dict):
        # Filter by user_id if needed
        for user_id in user_ids:
            await self.publish(event_type, {"user_id": user_id, **data})

notifications = NotificationManager()
