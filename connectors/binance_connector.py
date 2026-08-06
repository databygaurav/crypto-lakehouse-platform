from connectors.base_connector import BaseConnector
from clients.http_client import HTTPClient

class BinanceConnector(BaseConnector):

    BASE_URL = "https://api.binance.com"

    def authenticate(self):
        print("Authentication will be implemented later.")

    def get_balances(self):
        print("Balances will be implemented later.")

    def get_trades(self):
        print("Trades will be implemented later.")

    def get_server_time(self):
        url = f"{self.BASE_URL}/api/v3/time"

        return HTTPClient.get(url)