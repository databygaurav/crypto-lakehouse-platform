from connectors.base_connector import BaseConnector



class BinanceConnector(BaseConnector):

    def authenticate(self):
        print("Authenticating with Binance...")

    def get_balances(self):
        print("Fetching balances...")

    def get_trades(self):
        print("Fetching trades...")