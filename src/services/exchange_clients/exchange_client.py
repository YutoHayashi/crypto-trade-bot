from typing import Literal
from abc import ABC, abstractmethod

from ..exception import RuntimeException


class TransactionException(RuntimeException):
    """Base exception for transaction errors."""
    _title = "Transaction Exception"


class ExchangeClient(ABC):
    """
    Abstract base class for exchange APIs.
    This class defines the interface for interacting with different exchange APIs.
    """
    
    @property
    @abstractmethod
    def exchange_name(self) -> str:
        """
        Returns the name of the exchange.
        """
        pass
    
    @abstractmethod
    def get_ticker(self, symbol: str) -> dict:
        """
        Fetches the ticker information for a given symbol.
        """
        pass
    
    @abstractmethod
    def get_health(self, symbol: str) -> dict:
        """
        Fetches the health status of the exchange.
        This method can be extended to include more detailed health checks.
        """
        pass
    
    @abstractmethod
    def get_balance(self) -> list:
        """
        Fetches the balance of the account.
        """
        pass
    
    @abstractmethod
    def get_collateral(self) -> dict:
        """
        Fetches the collateral information of the account.
        """
        pass
    
    @abstractmethod
    def create_order(self, symbol: str, side: Literal["buy", "sell"], size: float, price: float = None, order_type: str = Literal["limit", "market"]) -> dict:
        """
        Creates a new order.
        """
        pass
    
    @abstractmethod
    def cancel_order(self, order_id: str, symbol: str = None) -> dict:
        """
        Cancels an existing order by its ID.
        """
        pass
    
    @abstractmethod
    def get_orders(self, symbol: str, order_state: str) -> list:
        """
        Fetches all orders or orders for a specific symbol.
        :param symbol: The product code for which to fetch the orders.
        :return: A list of orders.
        """
        pass
    
    @abstractmethod
    def get_positions(self, symbol: str) -> dict:
        """
        Fetches the positions for a given symbol.
        :param symbol: The product code for which to fetch the positions.
        :return: A dictionary containing position information.
        """
        pass