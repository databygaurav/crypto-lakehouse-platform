import unittest
from unittest.mock import Mock

from clients.binance_client import BinanceClient


class FundingWalletTests(unittest.TestCase):

    def setUp(self):
        self.http_client = Mock()
        self.client = BinanceClient(
            api_key="test-key",
            secret_key="test-secret",
            http_client=self.http_client,
        )
        self.client.get_server_time = Mock(
            return_value={"serverTime": 123456789}
        )

    def test_fetches_funding_wallet_balances(self):
        self.http_client.post.return_value = [
            {
                "asset": "USDT",
                "free": "3.80",
                "locked": "0"
            }
        ]

        result = self.client.get_funding_wallet()

        self.assertEqual(result[0]["asset"], "USDT")

        request = self.http_client.post.call_args.kwargs
        self.assertTrue(
            request["url"].endswith(
                "/sapi/v1/asset/get-funding-asset"
            )
        )
        self.assertEqual(
            request["data"]["needBtcValuation"],
            "false"
        )
        self.assertEqual(
            request["data"]["timestamp"],
            123456789
        )
        self.assertIn("signature", request["data"])
        self.assertIn("X-MBX-APIKEY", request["headers"])

    def test_rejects_invalid_funding_wallet_response(self):
        self.http_client.post.return_value = {
            "unexpected": "object"
        }

        with self.assertRaisesRegex(
            RuntimeError,
            "response must be a list"
        ):
            self.client.get_funding_wallet()


if __name__ == "__main__":
    unittest.main()
