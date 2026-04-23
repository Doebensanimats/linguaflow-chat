from fastapi import APIRouter
from models.message import Message
from services.message_service import save_message, get_messages

router = APIRouter()

@router.post("/send")
def send_message(msg: Message):
    save_message(msg)
    return {"status": "sent"}

@router.get("/messages")
def fetch_messages(room_id: str):
    return get_messages(room_id)