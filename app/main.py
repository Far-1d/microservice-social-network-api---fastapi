from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from routers import post, interactions, stats
from db import database

app = FastAPI()

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
