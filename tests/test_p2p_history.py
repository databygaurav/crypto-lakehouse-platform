import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock

from clients.binance_client import BinanceClient
from utils.history_fetcher import (
    generate_p2p_time_windows
)


class P2PWindowTests(unittest.TestCase):

    def test_windows_are_non_overlapping_and_at_most_30_days(self):
        start = datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc
        )
        end = start + timedelta(days=75)

        windows = generate_p2p_time_windows(
            start,
            end
        )

        self.assertEqual(len(windows), 3)

        for index, window in enumerate(windows):
            duration = (
                window["end_time"]
                - window["start_time"]
                + 1
            )

            self.assertLessEqual(
                duration,
                int(timedelta(days=30).total_seconds() * 1000)
            )

            if index:
                self.assertEqual(
                    windows[index - 1]["end_time"] + 1,
                    window["start_time"]
                )


class P2PPaginationTests(unittest.TestCase):

    def setUp(self):
        self.client = BinanceClient(
            api_key="test-key",
            secret_key="test-secret"
        )
        self.start = datetime(
            2026,
            8,
            1,
            tzinfo=timezone.utc
        )
        self.end = self.start + timedelta(days=1)

    def test_fetches_all_pages_and_deduplicates_orders(self):
        self.client.get_p2p_transactions = Mock(
            side_effect=[
                {
                    "code": "000000",
                    "message": "success",
                    "total": 3,
                    "data": [
                        {"orderNumber": "1"},
                        {"orderNumber": "2"}
                    ]
                },
                {
                    "code": "000000",
                    "message": "success",
                    "total": 3,
                    "data": [
                        {"orderNumber": "2"},
                        {"orderNumber": "3"}
                    ]
                }
            ]
        )

        records = self.client.get_all_p2p_transactions(
            trade_type="BUY",
            start_datetime=self.start,
            end_datetime=self.end,
            rows=2
        )

        self.assertEqual(
            [record["orderNumber"] for record in records],
            ["1", "2", "3"]
        )
        self.assertEqual(
            self.client.get_p2p_transactions.call_count,
            2
        )

    def test_raises_when_binance_returns_an_error(self):
        self.client.get_p2p_transactions = Mock(
            return_value={
                "code": "100001",
                "message": "invalid request"
            }
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "invalid request"
        ):
            self.client.get_all_p2p_transactions(
                trade_type="BUY",
                start_datetime=self.start,
                end_datetime=self.end
            )


if __name__ == "__main__":
    unittest.main()
