MESSAGES = []

def save_message(msg):
    MESSAGES.append(msg.dict())

def get_messages(room_id):
    return [m for m in MESSAGES if m["room_id"] == room_id]