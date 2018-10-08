import base64
import os.path
from unittest import TestCase

from . import main


class TestMain(TestCase):
    def test_push_small_data(self):
        refs = main.push_data(b"Hello, World!" * 100)
        print(refs)

    def test_push_data(self):
        with open(os.path.expanduser("~/Downloads/grumpycat.jpg"), "rb") as f:
            data = f.read()
        refs = main.push_data(data)
        print(refs)

    def test_pull_data(self):
        data = main.pull_data(base64.b64decode("sMyD5aX5fWuvfAnMKEkEhyrH6IsTLGNQt8b9JuFsbHc="),
                              base64.b64decode("7ollOJ1ehO1VH7bd10+MRA20+LMOrUf/TQnvE8OxlNo="))
        with open("foo.jpg", "wb") as f:
            f.write(data)
