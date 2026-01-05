from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import os, json, uuid, time
from typing import Dict, Optional
from dotenv import load_dotenv
import asyncio

load_dotenv()

class FollowersRequestManager:
    def __init__(self):
        self.producer = None

    async def startup(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=os.environ.get('KAFKA_URL', None),
            key_serializer=lambda k: str(k).encode('utf-8'),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            compression_type='gzip'
        )
        await self.producer.start()

    async def shutdown(self):
        """Called on FastAPI shutdown"""
        if self.producer:
            await self.producer.stop()

    async def request_data(self, user_id: str, topic: str):
        if not topic in ['request-followers', 'request-blocked-users']:
            return None
        
        correlation_id = str(uuid.uuid4())

        message = {
            "request_id": correlation_id,
            "user_id": user_id,
            "timestamp": time.time()
        }

        await self.producer.send_and_wait(
            topic, 
            key=correlation_id,
            value=message
        )

        return correlation_id

class FollowersResponseManager:
    def __init__(self):
        self.responses: Dict[str, dict] = {}
        self.consumer = None
        self.consumer_task = None

    async def startup(self):
        self.consumer = AIOKafkaConsumer(
            bootstrap_servers=os.environ.get("KAFKA_URL", ''),
            value_deserializer=lambda v: json.loads(v.decode()),
        )
        self.consumer.subscribe(['response-followers', 'response-blocked-users'])
        await self.consumer.start()

        self.consumer_task = asyncio.create_task(self._consume_responses())

    async def shutdown(self):
        """Called on FastAPI shutdown"""
        if self.consumer_task:
            self.consumer_task.cancel()

    async def _consume_responses(self):
        try:
            async for msg in self.consumer:
                print('--------------- new message topic: ', msg.topic)
                correlation_id = msg.key.decode()
                self.responses[correlation_id] = msg.value
        finally:
            self.consumer.stop()

    async def wait_for_response(self, correlation_id: str, timeout: float = 15.0) -> Optional[dict]:
        start = asyncio.get_event_loop().time()
        while asyncio.get_event_loop().time() - start < timeout:
            if correlation_id in self.responses:
                return self.responses.pop(correlation_id)
            
            await asyncio.sleep(0.1)
        return None

# Global instance
request_manager = FollowersRequestManager()
response_manager = FollowersResponseManager()