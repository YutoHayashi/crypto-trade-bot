from typing import List, Literal
import dataclasses
import asyncio

from dependency_injector.wiring import inject, Provide

from .exchange_client import ExchangeClient


@dataclasses.dataclass
class Order:
    product_code: str
    side: Literal['BUY', 'SELL']
    child_order_type: Literal['LIMIT', 'MARKET']
    price: float
    size: float
    child_order_acceptance_id: str
    id: int = None
    child_order_id: str = None
    average_price: float = None
    child_order_state: Literal['ACTIVE', 'COMPLETED', 'CANCELED', 'EXPIRED', 'REJECTED'] = 'ACTIVE'
    expire_date: str = None
    child_order_date: str = None
    outstanding_size: float = None
    cancel_size: float = None
    executed_size: float = None
    total_commission: float = None
    time_in_force: Literal['GTC', 'IOC', 'FOK'] = None


class OrderBook:
    """
    Service for managing order book operations.
    This service can be extended to include methods for adding, removing, or updating orders.
    """
    _orders: List[Order] = []
    
    @inject
    async def sync(self,
                   exchange_client: ExchangeClient = Provide['exchange_client']):
        """
        Synchronize the order book data.
        This method can be extended to fetch and update order book data from an external source.
        :param exchange_client: The ExchangeClient for fetching order book data.
        """
        async with self.lock:
            orders = exchange_client.get_orders(symbol=self.crypto_currency_code, order_state='ACTIVE')
            self._orders = [Order(**order) for order in orders]
    
    async def add(self, order: Order):
        """
        Add a new order to the order book.
        :param order: The order to be added.
        """
        async with self.lock:
            self._orders.append(order)
    
    async def complete(self, order_id: str) -> Order | None:
        """
        Complete the order with the given ID.
        :param order_id: The child_order_acceptance_id of the order to complete.
        :return: The updated order if found, else None.
        """
        async with self.lock:
            for order in self._orders:
                if order.child_order_acceptance_id == order_id and order.child_order_state == 'ACTIVE':
                    order.child_order_state = 'COMPLETED'
                    return order
            return None
    
    async def cancel(self, order_id: str) -> Order | None:
        """
        Cancel the order with the given ID.
        :param order_id: The child_order_acceptance_id of the order to cancel.
        :return: The updated order if found, else None.
        """
        async with self.lock:
            for order in self._orders:
                if order.child_order_acceptance_id == order_id and order.child_order_state == 'ACTIVE':
                    order.child_order_state = 'CANCELED'
                    return order
            return None
    
    async def get_orders(self) -> List[Order]:
        async with self.lock:
            return self._orders.copy()
    
    async def flush(self):
        async with self.lock:
            self._orders = [order for order in self._orders if order.child_order_state == 'ACTIVE']
    
    def __len__(self):
        return len(self._orders)
    
    @inject
    def __init__(self,
                 config: dict = Provide['config']):
        """
        Initialize the OrderBook service.
        This service can be extended to include methods for managing order book data.
        """
        self.lock = asyncio.Lock()
        self.legal_currency_code = config.get('legal_currency_code')
        self.crypto_currency_code = config.get('crypto_currency_code')