import time
import hmac
import hashlib
import requests
import json

from config.settings import (
    GIOTTUS_API_KEY,
    GIOTTUS_SECRET_KEY,
)


class GiottusClient:

    BASE_URL = "https://api.giottus.com"

    def __init__(self):

        self.api_key = GIOTTUS_API_KEY
        self.secret_key = GIOTTUS_SECRET_KEY

    # ========================================================
    # STRINGIFY VALUES
    # ========================================================

    def _stringify_value(self, value):

        if value is None:
            return ""
        
        if isinstance(value, bool):
            return str(value).lower()
        
        if isinstance(value, (dict, list)):
            return json.dumps(
                value,
                separators=(",", ":")
            )

        return str(value)

    # ========================================================
    # CANONICAL STRING
    # ========================================================

    def _canonical(self, params):

        if not isinstance(params, dict):
            return ""

        items = []

        for key in sorted(params.keys()):

            if key.lower() == "signature":
                continue

            value = params[key]

            if value is None:
                continue

            items.append(
                f"{key}={self._stringify_value(value)}"
            )

        return "&".join(items)

    # ========================================================
    # SIGNATURE
    # ========================================================

    def _sign(self, query=None, body=None):

        query = query or {}
        body = body or {}

        payload = (
            self._canonical(query)
            +
            self._canonical(body)
        )

        return hmac.new(
            self.secret_key.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()
    
    # ========================================================
    # PRIVATE GET REQUEST
    # ========================================================

    def _private_get(
        self,
        endpoint,
        extra_params=None
    ):

        for attempt in range(3):

            query = {
                "timestamp": str(
                    int(time.time() * 1000)
                ),
                "recvWindow": "5000"
            }

            if extra_params:
                query.update(extra_params)

            query["signature"] = self._sign(
                query=query,
                body={}
            )

            headers = {
                "X-GIOTTUS-APIKEY": self.api_key
            }

            response = requests.get(
                self.BASE_URL + endpoint,
                params=query,
                headers=headers,
                timeout=10
            )

            if response.status_code == 429:

                if attempt == 2:
                    raise requests.HTTPError(
                        "HTTP 429 from Giottus API",
                        response=response
                    )

                wait_seconds = float(
                    response.headers.get(
                        "Retry-After",
                        10
                    )
                )

                print(
                    f"Rate limited. Waiting "
                    f"{wait_seconds} seconds..."
                )

                time.sleep(wait_seconds)

                continue

            if not response.ok:
                raise requests.HTTPError(
                    f"HTTP {response.status_code} "
                    "from Giottus API",
                    response=response
                )

            return response.json()
    
    # ========================================================
    # FETCH BALANCE
    # ========================================================

    def get_balances(
            self,
            omit_zero_balances=True
    ):
        
        params = {
            "omitZeroBalances": self._stringify_value(
                omit_zero_balances
            )
        }

        return self._private_get(
            "/api/v1/wallet",
            params
        )
    
    # ========================================================
    # SPOT TRADES HISTORY
    # ========================================================

    def get_trades(
        self,
        symbol,
        order_id=None,
        start_time=None,
        end_time=None,
        from_id=None,
        limit=20
    ):

        params = {
            "symbol": symbol,
            "limit": limit,
        }

        if order_id is not None:
            params["orderId"] = order_id

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        if from_id is not None:
            params["fromId"] = from_id

        return self._private_get(
            "/api/v1/spot/trades",
            params
        )

    # ========================================================
    # HISTORICAL SPOT TRADES
    # ========================================================

    def get_historical_trades(
        self,
        symbol,
        order_id=None,
        start_time=None,
        end_time=None,
        from_id=None,
        limit=20
    ):

        params = {
            "symbol": symbol,
            "limit": limit,
        }

        if order_id is not None:
            params["orderId"] = order_id

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        if from_id is not None:
            params["fromId"] = from_id

        return self._private_get(
            "/api/v1/spot/trades/historical",
            params
        )

    # ========================================================
    # ALL SPOT TRADES
    # ========================================================

    def get_all_trades(
        self,
        symbol
    ):

        recent_trades = self.get_trades(
            symbol=symbol,
            limit=50
        )

        historical_trades = self.get_historical_trades(
            symbol=symbol,
            limit=50
        )

        combined_trades = (
            historical_trades
            +
            recent_trades
        )

        unique_trades = []
        seen_ids = set()

        for trade in combined_trades:

            trade_id = trade["id"]

            if trade_id not in seen_ids:
                seen_ids.add(trade_id)
                unique_trades.append(trade)

        unique_trades.sort(
            key=lambda trade: trade["time"]
        )

        return unique_trades

    # ========================================================
    # EASY BUY / SELL TRADES
    # ========================================================

    def get_ebes_trades(
        self,
        symbol,
        order_id=None,
        start_time=None,
        end_time=None,
        from_id=None,
        limit=20
    ):
        
        params = {
            "symbol": symbol,
            "limit": limit,
        }

        if order_id is not None:
            params["orderId"] = order_id

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        if from_id is not None:
            params["fromId"] = from_id

        return self._private_get(
            "/api/v1/ebes/trades",
            params
        )
    
    # ========================================================
    # HISTORICAL EASY BUY / SELL TRADES
    # ========================================================

    def get_historical_ebes_trades(
        self,
        symbol,
        order_id=None,
        start_time=None,
        end_time=None,
        from_id=None,
        limit=20
    ):
        
        params = {
            "symbol": symbol,
            "limit": limit,
        }

        if order_id is not None:
            params["orderId"] = order_id

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        if from_id is not None:
            params["fromId"] = from_id

        return self._private_get(
            "/api/v1/ebes/trades/historical",
            params
        )
    
    # ========================================================
    # ALL EBES TRADES
    # ========================================================

    def get_all_ebes_trades(
        self,
        symbol
    ):
        
        recent_ebes_trades = self.get_ebes_trades(
            symbol = symbol,
            limit = 20
        )

        historical_ebes_trades  = self.get_historical_ebes_trades(
            symbol = symbol,
            limit = 20
        )

        combined_ebes_trades = (
            recent_ebes_trades
            +
            historical_ebes_trades
        )

        unique_ebes_trades = []
        seen_ids = set()

        for trade in combined_ebes_trades:

            trade_id = trade["id"]

            if trade_id not in seen_ids:
                seen_ids.add(trade_id)
                unique_ebes_trades.append(trade)

        unique_ebes_trades.sort(
            key=lambda trade: trade["time"]
        )

        return unique_ebes_trades

    # ========================================================
    # CRYPTO DEPOSITS
    # ========================================================

    def get_crypto_deposits(
        self,
        asset=None,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):
        
        params = {
        "limit": limit,
        }

        if asset is not None:
            params["asset"] = asset

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/crypto/deposits",
            params
        )
    
    # ========================================================
    # HISTORICAL CRYPTO DEPOSITS
    # ========================================================

    def get_historical_crypto_deposits(
        self,
        asset=None,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if asset is not None:
            params["asset"] = asset

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/crypto/deposits/historical",
            params
        )
    
    # ========================================================
    # ALL CRYPTO DEPOSITS
    # ========================================================
    
    def get_all_crypto_deposits(
        self,
        asset=None
    ):
        
        recent_crypto_deposits = self.get_crypto_deposits(
            asset = asset,
            limit = 20
        )

        historical_crypto_deposits  = self.get_historical_crypto_deposits(
            asset = asset,
            limit = 20
        )

        combined_crypto_deposits = (
            recent_crypto_deposits
            +
            historical_crypto_deposits
        )

        unique_crypto_deposits = []
        seen_keys = set()

        for deposit in combined_crypto_deposits:

            deposit_key = (
                deposit.get("transactionHash"),
                deposit.get("asset"),
                deposit.get("time"),
                deposit.get("cryptoAmount")
            )

            if deposit_key not in seen_keys:
                seen_keys.add(deposit_key)
                unique_crypto_deposits.append(deposit)

        unique_crypto_deposits.sort(
            key=lambda deposit: deposit.get("time",0)
        )

        return unique_crypto_deposits
    
    # ========================================================
    # CRYPTO WITHDRAWALS
    # ========================================================

    def get_crypto_withdrawals(
        self,
        asset=None,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if asset is not None:
            params["asset"] = asset

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/crypto/withdrawals",
            params
        )


    # ========================================================
    # HISTORICAL CRYPTO WITHDRAWALS
    # ========================================================

    def get_historical_crypto_withdrawals(
        self,
        asset=None,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if asset is not None:
            params["asset"] = asset

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/crypto/withdrawals/historical",
            params
        )
    # ========================================================
    # ALL CRYPTO WITHDRAWALS
    # ========================================================

    def get_all_crypto_withdrawals(
            self,
            asset=None
    ):
        recent_crypto_withdrawals = self.get_crypto_withdrawals(
            asset=asset,
            limit=20
        )

        historical_crypto_withdrawals = self.get_historical_crypto_withdrawals(
            asset=asset,
            limit=20
        )

        combined_crypto_withdrawals = (
            recent_crypto_withdrawals
            +
            historical_crypto_withdrawals
        )

        unique_crypto_withdrawals = []
        seen_keys = set()

        for withdrawal in combined_crypto_withdrawals:

            withdrawal_key = (
                withdrawal.get("transactionHash"),
                withdrawal.get("asset"),
                withdrawal.get("time"),
                withdrawal.get("cryptoAmount")
            )

            if withdrawal_key not in seen_keys:
                seen_keys.add(withdrawal_key)
                unique_crypto_withdrawals.append(withdrawal)

        unique_crypto_withdrawals.sort(
            key=lambda withdrawal: withdrawal.get("time", 0)
        )

        return unique_crypto_withdrawals
    # ========================================================
    # FIAT DEPOSITS
    # ========================================================

    def get_fiat_deposits(
        self,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/fiat/deposits",
            params
        )


    # ========================================================
    # HISTORICAL FIAT DEPOSITS
    # ========================================================

    def get_historical_fiat_deposits(
        self,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/fiat/deposits/historical",
            params
        )
    
    # ========================================================
    # ALL FIAT DEPOSITS
    # ========================================================

    def get_all_fiat_deposits(
        self,
    ):
        
        recent_fiat_deposits = self.get_fiat_deposits(
            limit=20
        )

        historical_fiat_deposits = self.get_historical_fiat_deposits(
            limit=20
        )

        combined_fiat_deposits = (
            recent_fiat_deposits
            +
            historical_fiat_deposits
        )

        unique_fiat_deposits = []
        seen_keys = set()

        for deposit in combined_fiat_deposits:

            deposit_key = (
                deposit.get("referenceId"),
                deposit.get("time"),
                deposit.get("amount")
            )

            if deposit_key not in seen_keys:
                seen_keys.add(deposit_key)
                unique_fiat_deposits.append(deposit)

        unique_fiat_deposits.sort(
            key=lambda deposit: deposit.get("time",0)
        )

        return unique_fiat_deposits
    
    # ========================================================
    # FIAT WITHDRAWALS
    # ========================================================

    def get_fiat_withdrawals(
        self,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/fiat/withdrawals",
            params
        )


    # ========================================================
    # HISTORICAL FIAT WITHDRAWALS
    # ========================================================

    def get_historical_fiat_withdrawals(
        self,
        status=None,
        start_time=None,
        end_time=None,
        limit=20
    ):

        params = {
            "limit": limit,
        }

        if status is not None:
            params["status"] = status

        if start_time is not None:
            params["startTime"] = start_time

        if end_time is not None:
            params["endTime"] = end_time

        return self._private_get(
            "/api/v1/fiat/withdrawals/historical",
            params
        )
    
    # ========================================================
    # ALL FIAT WITHDRAWALS
    # ========================================================

    def get_all_fiat_withdrawals(
        self,
    ):
        
        recent_fiat_withdrawals = self.get_fiat_withdrawals(
            limit=20
        )

        historical_fiat_withdrawals = self.get_historical_fiat_withdrawals(
            limit=20
        )

        combined_fiat_withdrawals = (
            recent_fiat_withdrawals
            +
            historical_fiat_withdrawals
        )

        unique_fiat_withdrawals = []
        seen_keys = set()

        for withdrawal in combined_fiat_withdrawals:

            withdrawal_key = (
                withdrawal.get("referenceId"),
                withdrawal.get("time"),
                withdrawal.get("amount")
            )

            if withdrawal_key not in seen_keys:
                seen_keys.add(withdrawal_key)
                unique_fiat_withdrawals.append(withdrawal)

        unique_fiat_withdrawals.sort(
            key=lambda withdrawal: withdrawal.get("time",0)
        )

        return unique_fiat_withdrawals