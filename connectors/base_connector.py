from abc import ABC, abstractmethod

class BaseConnector(ABC):

    @abstractmethod
    def authenticate(self):
        pass

    @abstractmethod
    def get_balances(self):
        pass

    @abstractmethod
    def get_trades(self):
        pass