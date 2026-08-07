import time
from urllib.parse import urlencode

from clients.http_client import HTTPClient
from config.settings import (
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY,
)
from utils.signature import generate_signature


class BinanceClient:

    BASE_URL = "https://api.binance.com"

    def get_server_time(self):
        endpoint = "/api/v3/time"
        url = f"{self.BASE_URL}{endpoint}"

        return HTTPClient.get(url)

    def get_account(self):
        endpoint = "/api/v3/account"

        timestamp = int(time.time() * 1000)

        params = {
            "timestamp": timestamp
        }

        query_string = urlencode(params)

        signature = generate_signature(
            BINANCE_SECRET_KEY,
            query_string
        )

        params["signature"] = signature

        headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }

        url = f"{self.BASE_URL}{endpoint}"

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )