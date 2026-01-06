from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import post, interactions, stats, notifications
from db import database
from contextlib import asynccontextmanager
from core.communications import request_manager, response_manager
from core.cache import redis_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup code (runs before the app starts receiving requests)
    print("Starting up...")
    
    response_manager.app = app
    await response_manager.startup()
    await request_manager.startup()
    print('kafka is ready')

    await redis_client.ping()
    print('redis is ready')

    yield  # The app runs here
        
    await response_manager.shutdown()
    await request_manager.shutdown()
    print('kafka shutdown')

    await redis_client.close()
    print('redis shutdown')

    print("Shutdown complete!")


app = FastAPI(lifespan=lifespan)

origins = ['127.0.0.1', 'localhost']
app.add_middleware(CORSMiddleware,
                   allow_origins=origins,
                   allow_methods=['*'],
                   allow_headers=['*'],
                   )

database.Base.metadata.create_all(bind=database.engine)

app.include_router(post.router, prefix='/api')
app.include_router(interactions.router, prefix='/api')
app.include_router(stats.router, prefix='/api')
app.include_router(notifications.router, prefix='')
