import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from clients.binance_client import BinanceClient


class CapitalHistoryPaginationTests(unittest.TestCase):

    def setUp(self):
        self.client = BinanceClient(
            api_key="test-key",
            secret_key="test-secret"
        )
        self.end = datetime(
            2026,
            8,
            27,
            tzinfo=timezone.utc
        )

    @patch(
        "clients.binance_client.generate_time_windows",
        return_value=[{"start_time": 100, "end_time": 200}]
    )
    def test_fetches_every_deposit_page_and_deduplicates(self, _windows):
        self.client.get_deposit_history = Mock(
            side_effect=[
                [{"id": "a"}, {"id": "b"}],
                [{"id": "b"}]
            ]
        )

        records = self.client.get_all_deposits(
            start_datetime=datetime(
                2026,
                8,
                1,
                tzinfo=timezone.utc
            ),
            end_datetime=self.end,
            limit=2
        )

        self.assertEqual([record["id"] for record in records], ["a", "b"])
        self.assertEqual(
            [call.kwargs["offset"] for call in self.client.get_deposit_history.call_args_list],
            [0, 2]
        )

    @patch(
        "clients.binance_client.generate_time_windows",
        return_value=[{"start_time": 100, "end_time": 200}]
    )
    def test_fetches_every_withdrawal_page(self, _windows):
        self.client.get_withdrawal_history = Mock(
            side_effect=[
                [{"id": "a"}, {"id": "b"}],
                [{"id": "c"}]
            ]
        )

        records = self.client.get_all_withdrawals(
            start_datetime=datetime(
                2026,
                8,
                1,
                tzinfo=timezone.utc
            ),
            end_datetime=self.end,
            limit=2
        )

        self.assertEqual(
            [record["id"] for record in records],
            ["a", "b", "c"]
        )
        self.assertEqual(
            [call.kwargs["offset"] for call in self.client.get_withdrawal_history.call_args_list],
            [0, 2]
        )

    @patch(
        "clients.binance_client.generate_time_windows",
        return_value=[{"start_time": 100, "end_time": 200}]
    )
    def test_rejects_invalid_deposit_response(self, _windows):
        self.client.get_deposit_history = Mock(return_value={"code": -1})

        with self.assertRaises(RuntimeError):
            self.client.get_all_deposits(
                start_datetime=datetime(
                    2026,
                    8,
                    1,
                    tzinfo=timezone.utc
                ),
                end_datetime=self.end
            )


if __name__ == "__main__":
    unittest.main()
