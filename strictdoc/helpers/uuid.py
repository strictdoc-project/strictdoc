import uuid


def create_uuid() -> str:
    return uuid.uuid4().hex
