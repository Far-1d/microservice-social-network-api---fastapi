import asyncio
import json, uuid
from core.cache import redis_client
from db.database import SessionLocal
from models.post import UserReference
from datetime import datetime, timezone

class UserEventManager:
    def __init__(self):
        self.redis = redis_client
        self.task = None
        self.db = SessionLocal()

    async def startup(self):
        self.task = asyncio.create_task(self.listen_to_redis())

    async def shutdown(self):
        """Called on FastAPI shutdown"""
        if self.task:
            self.task.cancel()
            
    async def listen_to_redis(self):
        async with self.redis.pubsub() as pubsub:
            await pubsub.subscribe(f'user_events')
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True)
                if message:
                    dump = json.loads(message['data'])
                    _data = dump['data']
                    _type = dump['type']

                    print(f':::: {_type}, {message['data']}')
                    if _type == 'create':
                        await self._handle_create(_data)
                    elif _type == 'update':
                        await self._handle_update(_data)
                    elif _type == 'delete':
                        await self._handle_delete(_data)
                    
                await asyncio.sleep(1)

    async def _handle_create(self, user_data: dict):
        try:
            user_id = uuid.UUID(user_data['id'])

            existing_user = self.db.query(UserReference).filter(
                UserReference.user_id == user_id
            ).first()
            if existing_user:
                    return
            
            user = UserReference(
                user_id=user_id,
                username=user_data.get('username'),
                slug=user_data.get('slug'),
                email=user_data.get('email'),
                is_active=True,
                synced_at=datetime.now(timezone.utc)
            )
            self.db.add(user)
            self.db.commit()
        except Exception as e:
             print('create user exception : ', e)
    
    async def _handle_update(self, user_data: dict):
        try:
            user_id = uuid.UUID(user_data['id'])
            existing_user = self.db.query(UserReference).filter(
                UserReference.user_id == user_id
            ).first()

            if not existing_user:
                    await self._handle_create(user_data)
                    return

            existing_user.username=user_data.get('username')
            existing_user.slug=user_data.get('slug')
            existing_user.email=user_data.get('email')
            existing_user.synced_at=datetime.now(timezone.utc)
            
            self.db.add(existing_user)
            self.db.commit()
        except Exception as e:
             print('update user exception : ', e)

    async def _handle_delete(self, user_data: dict):
        try:
            user_id = uuid.UUID(user_data['id'])

            existing_user = await self.db.query(UserReference).filter(
                UserReference.user_id == user_id
            )
            if not existing_user:
                    return

            self.db.delete(existing_user)
            self.db.commit()
        except Exception as e:
             print('delete user exception : ', e)
        
user_events = UserEventManager()
