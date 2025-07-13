class StrictDocException(Exception):
    def __str__(self) -> str:
        return self.to_print_message()

    def to_print_message(self) -> str:
        return str(self.args[0])
