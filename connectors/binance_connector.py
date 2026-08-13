from connectors.base_connector import BaseConnector
from clients.binance_client import BinanceClient


class BinanceConnector(BaseConnector):

    def __init__(self):
        self.client = BinanceClient()

    # ========================================================
    # SERVER TIME
    # ========================================================

    def get_server_time(self):
        return self.client.get_server_time()

    # ========================================================
    # ACCOUNT
    # ========================================================

    def get_account(self):
        return self.client.get_account()

    # ========================================================
    # BALANCES
    # ========================================================

    def get_balances(self):
        account = self.client.get_account()
        return account.get("balances", [])

    # ========================================================
    # TRADES
    # ========================================================

    def get_trades(self, symbol):
        return self.client.get_trades(symbol)

    # ========================================================
    # P2P TRANSACTIONS
    # ========================================================

    def get_p2p_transactions(
        self,
        trade_type,
        page=1,
        rows=100,
        start_timestamp=None,
        end_timestamp=None
    ):
        return self.client.get_p2p_transactions(
            trade_type=trade_type,
            page=page,
            rows=rows,
            start_timestamp=start_timestamp,
            end_timestamp=end_timestamp
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
        return self.client.get_deposit_history(
            coin=coin,
            start_time=start_time,
            end_time=end_time
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
        return self.client.get_all_deposits(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            coin=coin
        )

    # ========================================================
    # WITHDRAWAL HISTORY
    # ========================================================

    def get_withdrawal_history(
        self,
        coin=None,
        start_time=None,
        end_time=None
    ):
        return self.client.get_withdrawal_history(
            coin=coin,
            start_time=start_time,
            end_time=end_time
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
        return self.client.get_all_withdrawals(
            start_datetime=start_datetime,
            end_datetime=end_datetime,
            coin=coin
        )

    # ========================================================
    # UNIVERSAL TRANSFER
    # ========================================================

    def get_transfer_history(
        self,
        transfer_type,
        start_time=None,
        end_time=None
    ):
        return self.client.get_transfer_history(
            transfer_type=transfer_type,
            start_time=start_time,
            end_time=end_time
        )

    # ========================================================
    # ALL UNIVERSAL TRANSFERS
    # ========================================================

    def get_all_transfers(
        self,
        end_datetime,
        transfer_type
    ):
        return self.client.get_all_transfers(
            end_datetime=end_datetime,
            transfer_type=transfer_type
        )

    # ========================================================
    # AUTHENTICATION
    # ========================================================

    def authenticate(self):
        print(
            "Authentication handled "
            "through Binance API credentials."
        )