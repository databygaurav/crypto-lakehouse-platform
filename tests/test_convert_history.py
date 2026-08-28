import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from clients.binance_client import BinanceClient
from utils.history_fetcher import (
    generate_convert_time_windows
)


class ConvertWindowTests(unittest.TestCase):

    def test_windows_are_non_overlapping_and_at_most_30_days(self):
        start = datetime(
            2026,
            1,
            1,
            tzinfo=timezone.utc
        )
        end = start + timedelta(days=61)

        windows = generate_convert_time_windows(
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


class ConvertPaginationTests(unittest.TestCase):

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
        self.start_ms = int(
            self.start.timestamp() * 1000
        )

    def test_fetches_continuation_and_deduplicates_orders(self):
        self.client.get_convert_trade_history = Mock(
            side_effect=[
                {
                    "list": [
                        {
                            "orderId": 1,
                            "toAsset": "SOL",
                            "toAmount": "1",
                            "createTime": self.start_ms + 1000
                        },
                        {
                            "orderId": 2,
                            "toAsset": "SOL",
                            "toAmount": "1",
                            "createTime": self.start_ms + 2000
                        }
                    ],
                    "moreData": True
                },
                {
                    "list": [
                        {
                            "orderId": 2,
                            "toAsset": "SOL",
                            "toAmount": "1",
                            "createTime": self.start_ms + 2000
                        },
                        {
                            "orderId": 3,
                            "toAsset": "SOL",
                            "toAmount": "1",
                            "createTime": self.start_ms + 3000
                        }
                    ],
                    "moreData": False
                }
            ]
        )

        records = self.client.get_all_convert_trades(
            start_datetime=self.start,
            end_datetime=self.end,
            limit=2
        )

        self.assertEqual(
            [record["orderId"] for record in records],
            [1, 2, 3]
        )
        self.assertEqual(
            self.client.get_convert_trade_history.call_count,
            2
        )

        second_call = (
            self.client.get_convert_trade_history
            .call_args_list[1]
            .kwargs
        )
        self.assertEqual(
            second_call["start_time"],
            self.start_ms + 2001
        )

    def test_rejects_more_data_without_records(self):
        self.client.get_convert_trade_history = Mock(
            return_value={
                "list": [],
                "moreData": True
            }
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "returned no records"
        ):
            self.client.get_all_convert_trades(
                start_datetime=self.start,
                end_datetime=self.end
            )

    @patch("clients.binance_client.HTTPClient.get")
    def test_signed_convert_request_uses_trade_flow_endpoint(
        self,
        mock_get
    ):
        mock_get.return_value = {
            "list": [],
            "moreData": False
        }
        self.client.get_server_time = Mock(
            return_value={"serverTime": 123456789}
        )

        self.client.get_convert_trade_history(
            start_time=100,
            end_time=200,
            limit=1000
        )

        request = mock_get.call_args.kwargs

        self.assertTrue(
            request["url"].endswith(
                "/sapi/v1/convert/tradeFlow"
            )
        )
        self.assertEqual(request["params"]["startTime"], 100)
        self.assertEqual(request["params"]["endTime"], 200)
        self.assertEqual(request["params"]["limit"], 1000)
        self.assertEqual(
            request["params"]["timestamp"],
            123456789
        )
        self.assertIn("signature", request["params"])
        self.assertIn("X-MBX-APIKEY", request["headers"])


if __name__ == "__main__":
    unittest.main()
