import asyncio

from dependency_injector.wiring import inject, Provide

from .exchange_client import ExchangeClient


class Portfolio:
    """
    Service for managing portfolio-related operations.
    This service can be extended to include methods for adding, removing, or updating portfolio items.
    """
    _legal_currency_amount: float
    _crypto_currency_amount: float
    _collateral_amount: float
    
    @inject
    async def sync(self, 
                   exchange_client: ExchangeClient = Provide['exchange_client']):
        """
        Synchronize the portfolio data.
        This method can be extended to fetch and update portfolio data from an external source.
        :param exchange_client: The ExchangeClient for fetching balance and collateral.
        """
        async with self.lock:
            balance = exchange_client.get_balance()
            collateral = exchange_client.get_collateral()
            
            self._legal_currency_amount = next(filter(lambda x: x['currency_code'] == self.legal_currency_code, balance), {}).get('amount', 0.0)
            self._crypto_currency_amount = next(filter(lambda x: x['currency_code'] == self.crypto_currency_code, balance), {}).get('amount', 0.0)
            self._collateral_amount = collateral.get('collateral', 0.0)
    
    async def get_legal_currency_amount(self) -> float:
        async with self.lock:
            return self._legal_currency_amount
    
    async def get_crypto_currency_amount(self) -> float:
        async with self.lock:
            return self._crypto_currency_amount
    
    async def get_collateral_amount(self) -> float:
        async with self.lock:
            return self._collateral_amount
    
    @inject
    def __init__(self,
                 config: dict = Provide['config']):
        """
        Initialize the PortfolioService with amounts and Bitflyer client.
        :param config: The application container configuration dictionary.
        """
        self.lock = asyncio.Lock()
        self.legal_currency_code = config.get('legal_currency_code')
        self.crypto_currency_code = config.get('crypto_currency_code')