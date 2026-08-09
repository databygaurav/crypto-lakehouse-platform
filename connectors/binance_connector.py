from connectors.base_connector import BaseConnector
from clients.binance_client import BinanceClient


class BinanceConnector(BaseConnector):

    def __init__(self):
        self.client = BinanceClient()

    def authenticate(self):
        print("Authentication will be implemented later.")

    def get_balances(self):
        print("Balances will be implemented later.")

    def get_trades(self, symbol):
        return self.client.get_trades(symbol)

    def get_server_time(self):
        return self.client.get_server_time()

    def get_account(self):
        return self.client.get_account()