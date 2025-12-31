from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base

# change to production level db
SQLALCHEMY_DATABASE_URL = 'sqlite:///db.sqlite3'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={'check_same_thread': False}   # only for sqlite
)

# Reflect existing tables (including Django's 'users')
metadata = MetaData()
metadata.reflect(bind=engine)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base(metadata=metadata)

def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
