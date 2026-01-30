import unittest
from app.utils import format_size


class TestUtils(unittest.TestCase):

    def test_format_size_valid(self):
        self.assertEqual(format_size(1048576), "1MB")

    def test_format_size_none(self):
        self.assertEqual(format_size(None), "Unknown size")


if __name__ == "__main__":
    unittest.main()
