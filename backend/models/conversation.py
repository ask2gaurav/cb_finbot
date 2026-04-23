from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class MessageModel(BaseModel):
    role: str
    content: str
    sources: List[dict] = []
    guardrail_flags: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)

class ConversationModel(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), alias="_id")
    user_id: str
    messages: List[MessageModel] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
