import unittest

from src.foo import foo


class TestFoo(unittest.TestCase):
    def test_foo(self):
        """
        @relation(REQ-1, scope=function)
        """
        assert foo()

    def test_second_method_in_class(self):
        """
        @relation(REQ-2, scope=function)
        """
        assert foo()

    @unittest.skipIf(False, "This test is never skipped")
    def test_with_decorator(self):
        """
        @relation(REQ-3, scope=function)
        """
        assert foo()

    @unittest.skipIf(False, "This test is never skipped")
    @unittest.skipUnless(True, "This test is never skipped")
    def test_with_multiple_decorators(self):
        """
        @relation(REQ-4, scope=function)
        """
        assert foo()
