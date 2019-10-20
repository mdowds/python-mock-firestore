import unittest
from datetime import datetime as dt

from mockfirestore.main import Timestamp


class TestTimestamp(unittest.TestCase):
    def test_timestamp(self):
        dt_timestamp = dt.now().timestamp()
        timestamp = Timestamp(dt_timestamp)

        seconds, nanos = str(dt_timestamp).split('.')
        self.assertEqual(seconds, timestamp.seconds)
        self.assertEqual(nanos, timestamp.nanos)

