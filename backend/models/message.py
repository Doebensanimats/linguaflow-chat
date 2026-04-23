from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    room_id: str
    user: str
    text: str
    lang: str
    timestamp: datetime | None = None