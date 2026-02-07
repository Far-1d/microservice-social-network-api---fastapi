from sqlalchemy import create_engine, MetaData
from sqlalchemy.dialects.sqlite import *
from sqlalchemy.orm import sessionmaker, Session, declarative_base
import os

# change to production level db
SQLALCHEMY_DATABASE_URL = 'sqlite:///db.sqlite3'

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={'check_same_thread': False}   # only for sqlite
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
        
