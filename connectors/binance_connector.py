from connectors.base_connector import BaseConnector
from clients.binance_client import BinanceClient


class BinanceConnector(BaseConnector):

    def __init__(self):
        self.client = BinanceClient()

    # -------------------------
    # Authentication
    # -------------------------

    def authenticate(self):
        print("Authentication will be implemented later.")

    # -------------------------
    # Balances
    # -------------------------

    def get_balances(self):
        print("Balances will be implemented later.")

    # -------------------------
    # Spot trades
    # -------------------------

    def get_trades(self, symbol):
        return self.client.get_trades(symbol)

    # -------------------------
    # Server time
    # -------------------------

    def get_server_time(self):
        return self.client.get_server_time()

    # -------------------------
    # Account
    # -------------------------

    def get_account(self):
        return self.client.get_account()

    # -------------------------
    # P2P transactions
    # -------------------------

    def get_p2p_transactions(
        self,
        trade_type="BUY",
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