from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.logging import setup_logging, get_logger

setup_logging()

from app.routers import post, interactions, stats, notifications
from app.db import database
from contextlib import asynccontextmanager
from app.core.communications import request_manager, response_manager
from app.core.cache import redis_client
from app.core.events import user_events
from app.logging_middleware import LoggingMiddleware
from app.metrics import setup_metrics
import logging



# disable uvicorn logs
logging.getLogger('uvicorn.access').disabled = True

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before the app starts receiving requests)
    print("Starting up...")
    
    response_manager.app = app
    await response_manager.startup()
    await request_manager.startup()
    print('kafka is ready')

    await redis_client.ping()
    await user_events.startup()
    print('redis is ready')
    
    yield  # The app runs here
    
    await response_manager.shutdown()
    await request_manager.shutdown()
    print('kafka shutdown')

    await user_events.shutdown()
    await redis_client.aclose()
    print('redis shutdown')

    print("Shutdown complete!")


app = FastAPI(lifespan=lifespan)

origins = ['127.0.0.1', 'localhost']
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=['*'],
                   allow_headers=['*'],
                   )

app.add_middleware(LoggingMiddleware)

setup_metrics(app)

database.Base.metadata.create_all(bind=database.engine)

app.include_router(post.router, prefix='/api')
app.include_router(interactions.router, prefix='/api')
app.include_router(stats.router, prefix='/api')
app.include_router(notifications.router, prefix='')
