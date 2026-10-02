"""Small CoinDCX client used to download current account balances."""

import hashlib
import hmac
import json
import time

from clients.http_client import HTTPClient
from config.settings import (
    COINDCX_API_KEY,
    COINDCX_SECRET_KEY,
)


class CoinDCXClient:

    BASE_URL = "https://api.coindcx.com"

    def __init__(self):
        self.api_key = COINDCX_API_KEY
        self.secret_key = COINDCX_SECRET_KEY

    def _check_credentials(self):
        if not self.api_key or not self.secret_key:
            raise ValueError(
                "CoinDCX API key and secret key are required"
            )

    def _sign(self, json_body):
        return hmac.new(
            self.secret_key.encode("utf-8"),
            json_body.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

    def _private_post(self, endpoint, body=None):
        """Sign and send one authenticated CoinDCX POST request."""

        self._check_credentials()

        request_body = dict(body or {})
        request_body["timestamp"] = int(time.time() * 1000)

        json_body = json.dumps(
            request_body,
            separators=(",", ":"),
        )

        headers = {
            "Content-Type": "application/json",
            "X-AUTH-APIKEY": self.api_key,
            "X-AUTH-SIGNATURE": self._sign(json_body),
        }

        return HTTPClient.post(
            self.BASE_URL + endpoint,
            data=json_body,
            headers=headers,
        )

    def get_balances(self):
        """Return current CoinDCX wallet balances."""

        return self._private_post(
            "/exchange/v1/users/balances"
        )
