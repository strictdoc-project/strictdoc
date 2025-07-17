import uuid


class MID(str):
    def __new__(cls, mid_value: str) -> "MID":
        assert isinstance(mid_value, str) and len(mid_value) > 0, mid_value
        return super().__new__(cls, mid_value)

    @staticmethod
    def create() -> "MID":
        return MID(uuid.uuid4().hex)

    def get_string_value(self) -> str:
        return str(self)
