import unittest
from datetime import datetime, timezone
from unittest.mock import Mock, patch

from clients.binance_client import BinanceClient


class TransferPaginationTests(unittest.TestCase):

    def setUp(self):
        self.client = BinanceClient(
            api_key="test-key",
            secret_key="test-secret"
        )

    @patch(
        "clients.binance_client.generate_time_windows",
        return_value=[{"start_time": 100, "end_time": 200}]
    )
    def test_fetches_every_transfer_page(
        self,
        _mock_windows
    ):
        self.client.get_transfer_history = Mock(
            side_effect=[
                {
                    "total": 3,
                    "rows": [
                        {"tranId": 1},
                        {"tranId": 2}
                    ]
                },
                {
                    "total": 3,
                    "rows": [
                        {"tranId": 3}
                    ]
                }
            ]
        )

        records = self.client.get_all_transfers(
            end_datetime=datetime(
                2026,
                8,
                27,
                tzinfo=timezone.utc
            ),
            transfer_type="MAIN_UMFUTURE",
            size=2
        )

        self.assertEqual(
            [record["tranId"] for record in records],
            [1, 2, 3]
        )
        self.assertEqual(
            [
                call.kwargs["current"]
                for call in self.client
                .get_transfer_history.call_args_list
            ],
            [1, 2]
        )
        self.assertTrue(
            all(
                record["transferType"] == "MAIN_UMFUTURE"
                for record in records
            )
        )


if __name__ == "__main__":
    unittest.main()
