import asyncio
from typing import Iterable
import json
from core.cache import redis_client

class NotificationManager:
    def __init__(self):
        self.redis = redis_client
    
    async def generate_message_stream(self, client_id:str):
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(f'notifications:{client_id}')
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    yield f"data: {message}\n\n"
                await asyncio.sleep(1)

    async def publish(self, user_id:str, event_type: str, data: dict):
        client_id = f"user_{user_id}"

        for k, v in data.items():
            data[k] = str(v)
        
        await self.redis.publish(
            f'notifications:{client_id}',
            json.dumps({
                "type": event_type,
                "data": data
            })
        )

    async def notify_user(self, user_id: str, event_type: str, data: dict):
        await self.publish(user_id, event_type, data)

    async def notify_users(self, user_ids: Iterable[str], event_type: str, data: dict):
        # Filter by user_id if needed
        for user_id in user_ids:
            await self.publish(user_id, event_type, data)

notifications = NotificationManager()
