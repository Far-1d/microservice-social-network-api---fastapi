from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional
import uuid

class BaseSchema(BaseModel):
    id: uuid.UUID
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)
