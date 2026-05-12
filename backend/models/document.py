from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid

class DocumentModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    filename: str
    filepath: str = "unknown"
    role: str
    uploaded_by: str
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "processing" # processing, completed, failed
    error: Optional[str] = None
