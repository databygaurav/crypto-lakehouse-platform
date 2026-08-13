from urllib.parse import urlencode

from clients.http_client import HTTPClient

from config.settings import (
    BINANCE_API_KEY,
    BINANCE_SECRET_KEY
)

from utils.signature import generate_signature

from utils.history_fetcher import (
    generate_time_windows,
    get_transfer_start_time
)


class BinanceClient:

    BASE_URL = "https://api.binance.com"

    # ========================================================
    # SERVER TIME
    # ========================================================

    def get_server_time(self):

        endpoint = "/api/v3/time"

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url
        )

    # ========================================================
    # ACCOUNT
    # ========================================================

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

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )

    # ========================================================
    # TRADES
    # ========================================================

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

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )

    # ========================================================
    # P2P TRANSACTIONS
    # ======================================================
    def get_p2p_transactions(
        self,
        trade_type,
        page=1,
        rows=100,
        start_timestamp=None,
        end_timestamp=None
    ):
        """
        Fetch Binance P2P transaction history.

        Returns the raw Binance API response dictionary.

        trade_type:
        BUY
        SELL
        """

        endpoint = (
        "/sapi/v1/c2c/"
        "orderMatch/listUserOrderHistory"
        )

        server_time = self.get_server_time()

        timestamp = server_time["serverTime"]

        params = {
            "tradeType": trade_type,
            "page": page,
            "rows": rows,
            "timestamp": timestamp
        }

        if start_timestamp is not None:
            params["startTimestamp"] = start_timestamp

        if end_timestamp is not None:
            params["endTimestamp"] = end_timestamp

        query_string = urlencode(params)

        signature = generate_signature(
            BINANCE_SECRET_KEY,
            query_string
        )

        params["signature"] = signature

        headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )
    # ========================================================
    # DEPOSIT HISTORY
    # ========================================================

    def get_deposit_history(
        self,
        coin=None,
        start_time=None,
        end_time=None
    ):

        endpoint = (
            "/sapi/v1/capital/"
            "deposit/hisrec"
        )

        server_time = self.get_server_time()

        timestamp = server_time["serverTime"]

        params = {
            "timestamp": timestamp
        }

        if coin is not None:
            params["coin"] = coin

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        query_string = urlencode(params)

        signature = generate_signature(
            BINANCE_SECRET_KEY,
            query_string
        )

        params["signature"] = signature

        headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )

    # ========================================================
    # ALL DEPOSITS
    # ========================================================

    def get_all_deposits(
        self,
        start_datetime,
        end_datetime,
        coin=None
    ):

        windows = generate_time_windows(
            start_datetime,
            end_datetime
        )

        all_deposits = []

        print(
            f"\nDeposit history windows: "
            f"{len(windows)}"
        )

        for index, window in enumerate(
            windows,
            start=1
        ):

            print(
                f"\nFetching deposit "
                f"window {index}/"
                f"{len(windows)}..."
            )

            response = self.get_deposit_history(
                coin=coin,
                start_time=window["start_time"],
                end_time=window["end_time"]
            )

            if isinstance(
                response,
                list
            ):

                print(
                    f"Records received: "
                    f"{len(response)}"
                )

                all_deposits.extend(
                    response
                )

        return all_deposits

    # ========================================================
    # WITHDRAWAL HISTORY
    # ========================================================

    def get_withdrawal_history(
        self,
        coin=None,
        start_time=None,
        end_time=None
    ):

        endpoint = (
            "/sapi/v1/capital/"
            "withdraw/history"
        )

        server_time = self.get_server_time()

        timestamp = server_time["serverTime"]

        params = {
            "timestamp": timestamp
        }

        if coin is not None:
            params["coin"] = coin

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        query_string = urlencode(params)

        signature = generate_signature(
            BINANCE_SECRET_KEY,
            query_string
        )

        params["signature"] = signature

        headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )

    # ========================================================
    # ALL WITHDRAWALS
    # ========================================================

    def get_all_withdrawals(
        self,
        start_datetime,
        end_datetime,
        coin=None
    ):

        windows = generate_time_windows(
            start_datetime,
            end_datetime
        )

        all_withdrawals = []

        print(
            f"\nWithdrawal history windows: "
            f"{len(windows)}"
        )

        for index, window in enumerate(
            windows,
            start=1
        ):

            print(
                f"\nFetching withdrawal "
                f"window {index}/"
                f"{len(windows)}..."
            )

            response = (
                self.get_withdrawal_history(
                    coin=coin,
                    start_time=window["start_time"],
                    end_time=window["end_time"]
                )
            )

            if isinstance(
                response,
                list
            ):

                print(
                    f"Records received: "
                    f"{len(response)}"
                )

                all_withdrawals.extend(
                    response
                )

        return all_withdrawals

    # ========================================================
    # UNIVERSAL TRANSFER
    # ========================================================

    def get_transfer_history(
        self,
        transfer_type,
        start_time=None,
        end_time=None
    ):

        endpoint = (
            "/sapi/v1/asset/transfer"
        )

        server_time = self.get_server_time()

        timestamp = server_time["serverTime"]

        params = {
            "type": transfer_type,
            "timestamp": timestamp
        }

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        query_string = urlencode(params)

        signature = generate_signature(
            BINANCE_SECRET_KEY,
            query_string
        )

        params["signature"] = signature

        headers = {
            "X-MBX-APIKEY": BINANCE_API_KEY
        }

        url = (
            f"{self.BASE_URL}"
            f"{endpoint}"
        )

        return HTTPClient.get(
            url=url,
            params=params,
            headers=headers
        )

    # ========================================================
    # ALL UNIVERSAL TRANSFERS
    # ========================================================

    def get_all_transfers(
        self,
        end_datetime,
        transfer_type
    ):

        transfer_start = (
            get_transfer_start_time(
                end_datetime
            )
        )

        windows = generate_time_windows(
            transfer_start,
            end_datetime
        )

        all_transfers = []

        print(
            f"\nTransfer history start:"
            f" {transfer_start}"
        )

        print(
            f"Transfer history end:"
            f" {end_datetime}"
        )

        print(
            f"Transfer history windows:"
            f" {len(windows)}"
        )

        for index, window in enumerate(
            windows,
            start=1
        ):

            print(
                f"\nFetching transfer "
                f"window {index}/"
                f"{len(windows)}..."
            )

            response = (
                self.get_transfer_history(
                    transfer_type=transfer_type,
                    start_time=window["start_time"],
                    end_time=window["end_time"]
                )
            )

            if not isinstance(
                response,
                dict
            ):
                continue

            records = response.get(
                "rows",
                []
            )

            print(
                f"Records received: "
                f"{len(records)}"
            )

            for record in records:

                record = dict(record)

                record[
                    "transferType"
                ] = transfer_type

                all_transfers.append(
                    record
                )

        return all_transfers