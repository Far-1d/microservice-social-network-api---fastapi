from sqlalchemy import Column, Integer, String, ForeignKey, UUID, DateTime, Boolean
import uuid
from datetime import datetime, timezone
from db import database

class BaseModel(database.Base):
    __abstract__ = True  

    id = Column(UUID, primary_key=True, default=uuid.uuid4, index=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=True)
    soft_delete = Column(Boolean, default=False)