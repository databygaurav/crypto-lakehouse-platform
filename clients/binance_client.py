from urllib.parse import urlencode

from clients.http_client import HTTPClient
from config.settings import (
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY,
)
from utils.signature import generate_signature


class BinanceClient:

    BASE_URL = "https://api.binance.com"

    # -------------------------
    # Server time
    # -------------------------

    def get_server_time(self):
        endpoint = "/api/v3/time"
        url = f"{self.BASE_URL}{endpoint}"

        return HTTPClient.get(url)

    # -------------------------
    # Account
    # -------------------------

    def get_account(self):
        endpoint = "/api/v3/account"

        server_time = self.get_server_time()
        timestamp = server_time["serverTime"]

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

    # -------------------------
    # Spot trades
    # -------------------------

    def get_trades(self, symbol):
        endpoint = "/api/v3/myTrades"

        server_time = self.get_server_time()
        timestamp = server_time["serverTime"]

        params = {
            "symbol": symbol,
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

    # -------------------------
    # P2P / C2C transactions
    # -------------------------

    def get_p2p_transactions(
        self,
        trade_type="BUY",
        page=1,
        rows=100,
        start_timestamp=None,
        end_timestamp=None
    ):

        endpoint = "/sapi/v1/c2c/orderMatch/listUserOrderHistory"

        server_time = self.get_server_time()
        timestamp = server_time["serverTime"]

        params = {
            "tradeType": trade_type,
            "page": page,
            "rows": rows,
            "timestamp": timestamp
        }

        # Add date range only when provided
        if start_timestamp is not None:
            params["startTimestamp"] = start_timestamp

        if end_timestamp is not None:
            params["endTimestamp"] = end_timestamp

        # Create query string
        query_string = urlencode(params)

        # Generate Binance signature
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