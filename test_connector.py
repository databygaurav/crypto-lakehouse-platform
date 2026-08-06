from connectors.binance_connector import BinanceConnector

connector = BinanceConnector()

server_time = connector.get_server_time()
print(server_time)