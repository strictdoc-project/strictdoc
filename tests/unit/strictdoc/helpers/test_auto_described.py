from strictdoc.helpers.auto_described import auto_described


def test_auto_described():
    class Example_OtherClass:
        pass

    @auto_described
    class Example:
        def __init__(self):
            self.dict_var: dict = {}
            self.set_var: set = set()
            self.bytes_var: bytes = b""
            self.int_var: int = 5
            self.other_class_var: Example_OtherClass = Example_OtherClass()

    example = Example()

    expected_string = "Example(dict_var = {}, set_var = set(0 elements), bytes_var = b'', int_var = 5, other_class_var = Example_OtherClass(...))"
    assert example.__str__() == expected_string
    assert example.__repr__() == expected_string
