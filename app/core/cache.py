import functools
import time
from typing import Callable, Any
import json
import os
import uuid
import datetime
from typing import AsyncGenerator
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", None)
redis_client = redis.from_url(
    REDIS_URL,
    decode_responses=True
)

async def get_redis() -> AsyncGenerator[redis.Redis, None]:
    yield redis_client

async def cache(ttl: int = 60*15):  # 15 min default
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # Generate cache key
            key = f"cache:{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try cache first
            cached = await redis_client.get(key)
            if cached:
                print(f"Cache HIT: {key}")
                return json.loads(cached)
            
            # Cache miss → call function
            result = await func(*args, **kwargs)
            
            # Cache result
            await redis_client.setex(key, ttl, json.dumps(result))
            print(f"Cache MISS → stored: {key}")
            
            return result
        return wrapper
    return decorator

