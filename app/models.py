import uuid
from datetime import datetime


def create_record(name: str, email: str, phone: str) -> dict:
    return {
        "id": str(uuid.uuid4()),
        "name": name,
        "email": email,
        "phone": phone,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
