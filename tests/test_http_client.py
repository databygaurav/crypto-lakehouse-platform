import unittest
from unittest.mock import Mock, patch

import requests

from clients.http_client import HTTPClient


class HTTPClientTests(unittest.TestCase):

    @patch.object(HTTPClient._session, "get")
    def test_uses_bounded_timeout_and_returns_json(self, mock_get):
        response = Mock(ok=True)
        response.json.return_value = {"ok": True}
        mock_get.return_value = response

        result = HTTPClient.get("https://example.test")

        self.assertEqual(result, {"ok": True})
        self.assertEqual(
            mock_get.call_args.kwargs["timeout"],
            (5, 30)
        )

    @patch.object(HTTPClient._session, "get")
    def test_error_does_not_include_signed_url(self, mock_get):
        response = Mock(ok=False, status_code=429)
        mock_get.return_value = response

        with self.assertRaisesRegex(
            requests.HTTPError,
            "HTTP 429 from remote API"
        ) as context:
            HTTPClient.get(
                "https://example.test",
                params={"signature": "secret-signature"}
            )

        self.assertNotIn(
            "secret-signature",
            str(context.exception)
        )

    @patch.object(HTTPClient._session, "post")
    def test_post_uses_bounded_timeout_and_returns_json(
        self,
        mock_post
    ):
        response = Mock(ok=True)
        response.json.return_value = [{"asset": "USDT"}]
        mock_post.return_value = response

        result = HTTPClient.post(
            "https://example.test",
            data={"timestamp": 123}
        )

        self.assertEqual(result, [{"asset": "USDT"}])
        self.assertEqual(
            mock_post.call_args.kwargs["timeout"],
            (5, 30)
        )


if __name__ == "__main__":
    unittest.main()
