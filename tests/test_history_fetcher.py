import unittest
from datetime import datetime, timedelta, timezone

from utils.history_fetcher import generate_time_windows


class HistoryWindowTests(unittest.TestCase):

    def test_general_windows_are_non_overlapping(self):
        start = datetime(2026, 1, 1, tzinfo=timezone.utc)
        windows = generate_time_windows(
            start,
            start + timedelta(days=180)
        )

        self.assertEqual(len(windows), 3)

        for current, following in zip(windows, windows[1:]):
            self.assertEqual(
                current["end_time"] + 1,
                following["start_time"]
            )


if __name__ == "__main__":
    unittest.main()
