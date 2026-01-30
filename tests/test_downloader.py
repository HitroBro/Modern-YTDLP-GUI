import unittest
from app.downloader import fetch_video_info


class TestDownloader(unittest.TestCase):

    def test_invalid_url(self):
        with self.assertRaises(Exception):
            fetch_video_info("invalid_url")


if __name__ == "__main__":
    unittest.main()
