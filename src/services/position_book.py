from typing import List, Literal
import dataclasses
import asyncio

from dependency_injector.wiring import inject, Provide

from .exchange_client import ExchangeClient


@dataclasses.dataclass
class Position:
    product_code: str
    side: Literal['BUY', 'SELL']
    price: float
    size: float
    commission: float = None
    swap_point_accumulate: float = None
    require_collateral: float = None
    open_date: str = None
    leverage: float = None
    pnl: float = None
    sfd: float = None


class PositionBook:
    """
    Service for managing position book operations.
    This service can be extended to include methods for adding, removing, or updating positions.
    """
    _positions: List[Position] = []
    
    @inject
    async def sync(self,
                   exchange_client: ExchangeClient = Provide['exchange_client']):
        """
        Synchronize the position book data.
        This method can be extended to fetch and update position book data from an external source.
        :param exchange_client: The ExchangeClient for fetching position book data.
        """
        async with self.lock:
            positions = exchange_client.get_positions(symbol=self.crypto_currency_code)
            self._positions = [Position(**position) for position in positions]
    
    async def add_and_settle(self, position: Position) -> float:
        """
        Add a new position to the position book.
        If an opposite position exists, offset (close) it as needed.
        :param position: The position to be added.
        :return: The realized PnL from offsetting, if any.
        """
        async with self.lock:
            pnl = 0.0
            for existing in self._positions:
                if existing.side != position.side:
                    if existing.size > position.size:
                        offset_size = position.size
                        pnl += (position.price - existing.price) * offset_size if position.side == 'SELL' else (existing.price - position.price) * offset_size
                        existing.size -= offset_size
                        return pnl
                    elif existing.size == position.size:
                        offset_size = position.size
                        pnl += (position.price - existing.price) * offset_size if position.side == 'SELL' else (existing.price - position.price) * offset_size
                        self._positions.remove(existing)
                        return pnl
                    elif existing.size < position.size:
                        offset_size = existing.size
                        pnl += (position.price - existing.price) * offset_size if position.side == 'SELL' else (existing.price - position.price) * offset_size
                        position.size -= offset_size
                        self._positions.remove(existing)
            self._positions.append(position)
            return pnl
    
    async def get_positions(self) -> List[Position]:
        async with self.lock:
            return self._positions.copy()
    
    @inject
    def __init__(self,
                 config: dict = Provide['config']):
        """
        Initialize the PositionBook service.
        This service can be extended to include methods for managing position book data.
        """
        self.lock = asyncio.Lock()
        self.legal_currency_code = config.get('legal_currency_code')
        self.crypto_currency_code = config.get('crypto_currency_code')