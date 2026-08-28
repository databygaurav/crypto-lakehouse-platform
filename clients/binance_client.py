"""Small Binance API client used by the ingestion script.

The public ``get_all_*`` methods are the ones a beginner normally needs.
They hide signing, time windows, pagination, and duplicate removal.
"""

from urllib.parse import urlencode

from clients.http_client import HTTPClient
from config.settings import BINANCE_API_KEY, BINANCE_SECRET_KEY
from utils.history_fetcher import (
    generate_convert_time_windows,
    generate_p2p_time_windows,
    generate_time_windows,
    get_transfer_start_time,
)
from utils.signature import generate_signature


def _check_limit(value, maximum, name="limit"):
    """Fail early when a Binance page size is invalid."""

    if value < 1 or value > maximum:
        raise ValueError(
            f"{name} must be between 1 and {maximum}"
        )


class BinanceClient:
    """Read account and history data from Binance."""

    BASE_URL = "https://api.binance.com"

    def __init__(
        self,
        api_key=BINANCE_API_KEY,
        secret_key=BINANCE_SECRET_KEY,
        http_client=HTTPClient,
    ):
        if not api_key or not secret_key:
            raise ValueError(
                "Binance API credentials are required. "
                "Add them to your .env file."
            )

        self.api_key = api_key
        self.secret_key = secret_key
        self.http_client = http_client

    # -----------------------------------------------------------------
    # Request helpers
    # -----------------------------------------------------------------

    def get_server_time(self):
        """Return Binance server time."""

        return self.http_client.get(
            url=f"{self.BASE_URL}/api/v3/time"
        )

    def _signed_get(self, endpoint, **params):
        """Send one authenticated GET request to Binance."""

        # Do not send optional parameters whose value is None.
        params = {
            name: value
            for name, value in params.items()
            if value is not None
        }

        server_time = self.get_server_time()
        params["timestamp"] = server_time["serverTime"]

        query_string = urlencode(params)
        params["signature"] = generate_signature(
            self.secret_key,
            query_string,
        )

        return self.http_client.get(
            url=f"{self.BASE_URL}{endpoint}",
            params=params,
            headers={"X-MBX-APIKEY": self.api_key},
        )

    # -----------------------------------------------------------------
    # Account and Spot trades
    # -----------------------------------------------------------------

    def get_account(self):
        """Fetch the current Binance account snapshot."""

        return self._signed_get("/api/v3/account")

    def get_trades(self, symbol, from_id=None, limit=1000):
        """Fetch one page of Spot trades."""

        _check_limit(limit, 1000)

        return self._signed_get(
            "/api/v3/myTrades",
            symbol=symbol,
            fromId=from_id,
            limit=limit,
        )

    def get_all_trades(self, symbol, limit=1000):
        """Fetch every available Spot trade for one symbol."""

        _check_limit(limit, 1000)
        trades = []
        seen_ids = set()
        next_trade_id = 0

        while True:
            page = self.get_trades(
                symbol=symbol,
                from_id=next_trade_id,
                limit=limit,
            )

            if not isinstance(page, list):
                raise RuntimeError(
                    "Binance spot-trade response must be a list"
                )

            if not page:
                break

            page_ids = []

            for trade in page:
                if not isinstance(trade, dict):
                    raise RuntimeError(
                        "Binance spot-trade record is invalid"
                    )

                try:
                    trade_id = int(trade["id"])
                except (KeyError, TypeError, ValueError) as error:
                    raise RuntimeError(
                        "Binance spot trade ID is invalid"
                    ) from error

                page_ids.append(trade_id)

                if trade_id not in seen_ids:
                    seen_ids.add(trade_id)
                    trades.append(trade)

            if len(page) < limit:
                break

            new_trade_id = max(page_ids) + 1

            if new_trade_id <= next_trade_id:
                raise RuntimeError(
                    "Spot-trade pagination did not advance"
                )

            next_trade_id = new_trade_id

        return trades

    # -----------------------------------------------------------------
    # Convert trades
    # -----------------------------------------------------------------

    def get_convert_trade_history(
        self,
        start_time,
        end_time,
        limit=1000,
    ):
        """Fetch one page of Binance Convert trades."""

        _check_limit(limit, 1000)

        return self._signed_get(
            "/sapi/v1/convert/tradeFlow",
            startTime=start_time,
            endTime=end_time,
            limit=limit,
        )

    def get_all_convert_trades(
        self,
        start_datetime,
        end_datetime,
        limit=1000,
    ):
        """Fetch all Convert trades in safe 30-day windows."""

        _check_limit(limit, 1000)
        trades = []
        seen_ids = set()

        for window in generate_convert_time_windows(
            start_datetime,
            end_datetime,
        ):
            current_start = window["start_time"]
            window_end = window["end_time"]

            while current_start <= window_end:
                response = self.get_convert_trade_history(
                    start_time=current_start,
                    end_time=window_end,
                    limit=limit,
                )

                if not isinstance(response, dict):
                    raise RuntimeError(
                        "Binance Convert returned an invalid response"
                    )

                page = response.get("list", [])
                more_data = response.get("moreData", False)

                if not isinstance(page, list):
                    raise RuntimeError(
                        "Binance Convert response list is invalid"
                    )

                if not isinstance(more_data, bool):
                    raise RuntimeError(
                        "Binance Convert moreData flag is invalid"
                    )

                for trade in page:
                    if not isinstance(trade, dict):
                        raise RuntimeError(
                            "Binance Convert record is invalid"
                        )

                    trade_id = (
                        trade.get("orderId")
                        or trade.get("quoteId")
                    )

                    if trade_id is None or trade_id not in seen_ids:
                        trades.append(trade)

                    if trade_id is not None:
                        seen_ids.add(trade_id)

                if not more_data:
                    break

                if not page:
                    raise RuntimeError(
                        "Binance Convert pagination returned no records"
                    )

                try:
                    last_time = max(
                        int(trade["createTime"])
                        for trade in page
                    )
                except (KeyError, TypeError, ValueError) as error:
                    raise RuntimeError(
                        "Binance Convert createTime is invalid"
                    ) from error

                new_start = last_time + 1

                if new_start <= current_start:
                    raise RuntimeError(
                        "Binance Convert pagination did not advance"
                    )

                current_start = new_start

        return trades

    # -----------------------------------------------------------------
    # P2P history
    # -----------------------------------------------------------------

    def get_p2p_transactions(
        self,
        trade_type,
        page=1,
        rows=100,
        start_timestamp=None,
        end_timestamp=None,
    ):
        """Fetch one page of Binance P2P orders."""

        _check_limit(rows, 100, name="rows")

        return self._signed_get(
            "/sapi/v1/c2c/orderMatch/listUserOrderHistory",
            tradeType=trade_type,
            page=page,
            rows=rows,
            startTimestamp=start_timestamp,
            endTimestamp=end_timestamp,
        )

    def get_all_p2p_transactions(
        self,
        trade_type,
        start_datetime,
        end_datetime,
        rows=100,
    ):
        """Fetch all P2P orders using windows and page numbers."""

        _check_limit(rows, 100, name="rows")
        orders = []
        seen_ids = set()

        for window in generate_p2p_time_windows(
            start_datetime,
            end_datetime,
        ):
            page_number = 1

            while True:
                response = self.get_p2p_transactions(
                    trade_type=trade_type,
                    page=page_number,
                    rows=rows,
                    start_timestamp=window["start_time"],
                    end_timestamp=window["end_time"],
                )

                if not isinstance(response, dict):
                    raise RuntimeError(
                        "Binance P2P returned an invalid response"
                    )

                if response.get("code") != "000000":
                    message = response.get(
                        "message",
                        "unknown Binance P2P error",
                    )
                    raise RuntimeError(
                        f"Binance P2P request failed: {message}"
                    )

                page = response.get("data", [])

                if not isinstance(page, list):
                    raise RuntimeError(
                        "Binance P2P response data must be a list"
                    )

                try:
                    total = int(response.get("total", len(page)))
                except (TypeError, ValueError) as error:
                    raise RuntimeError(
                        "Binance P2P response total is invalid"
                    ) from error

                for order in page:
                    if not isinstance(order, dict):
                        raise RuntimeError(
                            "Binance P2P record is invalid"
                        )

                    order_id = order.get("orderNumber")

                    if order_id is None or order_id not in seen_ids:
                        orders.append(order)

                    if order_id is not None:
                        seen_ids.add(order_id)

                if (
                    not page
                    or len(page) < rows
                    or page_number * rows >= total
                ):
                    break

                page_number += 1

        return orders

    # -----------------------------------------------------------------
    # Deposits and withdrawals
    # -----------------------------------------------------------------

    def get_deposit_history(
        self,
        coin=None,
        start_time=None,
        end_time=None,
        offset=0,
        limit=1000,
    ):
        """Fetch one page of crypto deposits."""

        if offset < 0:
            raise ValueError("offset must not be negative")

        _check_limit(limit, 1000)

        return self._signed_get(
            "/sapi/v1/capital/deposit/hisrec",
            coin=coin,
            startTime=start_time,
            endTime=end_time,
            offset=offset,
            limit=limit,
        )

    def get_withdrawal_history(
        self,
        coin=None,
        start_time=None,
        end_time=None,
        offset=0,
        limit=1000,
    ):
        """Fetch one page of crypto withdrawals."""

        if offset < 0:
            raise ValueError("offset must not be negative")

        _check_limit(limit, 1000)

        return self._signed_get(
            "/sapi/v1/capital/withdraw/history",
            coin=coin,
            startTime=start_time,
            endTime=end_time,
            offset=offset,
            limit=limit,
        )

    def _get_all_capital_records(
        self,
        fetch_page,
        record_name,
        start_datetime,
        end_datetime,
        coin,
        limit,
    ):
        """Shared offset pagination for deposits and withdrawals."""

        _check_limit(limit, 1000)
        records = []
        seen_ids = set()

        for window in generate_time_windows(
            start_datetime,
            end_datetime,
        ):
            offset = 0

            while True:
                page = fetch_page(
                    coin=coin,
                    start_time=window["start_time"],
                    end_time=window["end_time"],
                    offset=offset,
                    limit=limit,
                )

                if not isinstance(page, list):
                    raise RuntimeError(
                        f"Binance {record_name} response must be a list"
                    )

                for record in page:
                    if not isinstance(record, dict):
                        raise RuntimeError(
                            f"Binance {record_name} record is invalid"
                        )

                    record_id = record.get("id")

                    if record_id is None or record_id not in seen_ids:
                        records.append(record)

                    if record_id is not None:
                        seen_ids.add(record_id)

                if len(page) < limit:
                    break

                offset += len(page)

        return records

    def get_all_deposits(
        self,
        start_datetime,
        end_datetime,
        coin=None,
        limit=1000,
    ):
        """Fetch all deposits in the requested date range."""

        return self._get_all_capital_records(
            fetch_page=self.get_deposit_history,
            record_name="deposit",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            coin=coin,
            limit=limit,
        )

    def get_all_withdrawals(
        self,
        start_datetime,
        end_datetime,
        coin=None,
        limit=1000,
    ):
        """Fetch all withdrawals in the requested date range."""

        return self._get_all_capital_records(
            fetch_page=self.get_withdrawal_history,
            record_name="withdrawal",
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            coin=coin,
            limit=limit,
        )

    # -----------------------------------------------------------------
    # Universal transfers
    # -----------------------------------------------------------------

    def get_transfer_history(
        self,
        transfer_type,
        start_time=None,
        end_time=None,
        current=1,
        size=100,
    ):
        """Fetch one page of Universal Transfer history."""

        if current < 1:
            raise ValueError("current must be at least 1")

        _check_limit(size, 100, name="size")

        return self._signed_get(
            "/sapi/v1/asset/transfer",
            type=transfer_type,
            startTime=start_time,
            endTime=end_time,
            current=current,
            size=size,
        )

    def get_all_transfers(
        self,
        end_datetime,
        transfer_type,
        size=100,
    ):
        """Fetch available transfers from Binance's six-month history."""

        _check_limit(size, 100, name="size")
        start_datetime = get_transfer_start_time(end_datetime)
        transfers = []
        seen_ids = set()

        for window in generate_time_windows(
            start_datetime,
            end_datetime,
        ):
            page_number = 1

            while True:
                response = self.get_transfer_history(
                    transfer_type=transfer_type,
                    start_time=window["start_time"],
                    end_time=window["end_time"],
                    current=page_number,
                    size=size,
                )

                if not isinstance(response, dict):
                    raise RuntimeError(
                        "Binance transfer response must be a dictionary"
                    )

                page = response.get("rows", [])

                if not isinstance(page, list):
                    raise RuntimeError(
                        "Binance transfer rows must be a list"
                    )

                try:
                    total = int(response.get("total", len(page)))
                except (TypeError, ValueError) as error:
                    raise RuntimeError(
                        "Binance transfer total is invalid"
                    ) from error

                for transfer in page:
                    if not isinstance(transfer, dict):
                        raise RuntimeError(
                            "Binance transfer record is invalid"
                        )

                    transfer = dict(transfer)
                    transfer["transferType"] = transfer_type
                    transfer_id = transfer.get("tranId")

                    if transfer_id is None or transfer_id not in seen_ids:
                        transfers.append(transfer)

                    if transfer_id is not None:
                        seen_ids.add(transfer_id)

                if (
                    not page
                    or len(page) < size
                    or page_number * size >= total
                ):
                    break

                page_number += 1

        return transfers

    # -----------------------------------------------------------------
    # Price candles
    # -----------------------------------------------------------------

    def get_klines(
        self,
        symbol,
        interval="1m",
        start_time=None,
        end_time=None,
        limit=1000,
    ):
        """Fetch one page of public candlestick data."""

        _check_limit(limit, 1000)
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self.http_client.get(
            url=f"{self.BASE_URL}/api/v3/klines",
            params=params,
        )
