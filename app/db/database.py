from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

# change to production level db
NAME = os.environ.get('POSTGRES_DB')
USER = os.environ.get('POSTGRES_USER')
PASSWORD = os.environ.get('POSTGRES_PASSWORD')
HOST = os.environ.get('POSTGRES_HOST')
PORT = os.environ.get('POSTGRES_PORT')

POSTGRES_DATABSE_URL = f'postgresql://{USER}:{PASSWORD}@{HOST}:{PORT}/{NAME}'

engine = create_engine(
    POSTGRES_DATABSE_URL, 
)

metadata = MetaData()
Base = declarative_base()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
