import unittest
from unittest.mock import Mock

from clients.binance_client import BinanceClient


class SpotTradePaginationTests(unittest.TestCase):

    def setUp(self):
        self.client = BinanceClient(
            api_key="test-key",
            secret_key="test-secret"
        )

    def test_fetches_all_pages_from_the_oldest_trade(self):
        self.client.get_trades = Mock(
            side_effect=[
                [{"id": 1}, {"id": 2}],
                [{"id": 3}, {"id": 4}],
                [{"id": 5}]
            ]
        )

        trades = self.client.get_all_trades(
            symbol="SOLUSDT",
            limit=2
        )

        self.assertEqual(
            [trade["id"] for trade in trades],
            [1, 2, 3, 4, 5]
        )
        self.assertEqual(
            [
                call.kwargs["from_id"]
                for call in self.client.get_trades.call_args_list
            ],
            [0, 3, 5]
        )

    def test_rejects_invalid_response(self):
        self.client.get_trades = Mock(
            return_value={"code": -1}
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "response must be a list"
        ):
            self.client.get_all_trades("SOLUSDT")


if __name__ == "__main__":
    unittest.main()
