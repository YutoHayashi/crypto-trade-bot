from typing import Literal
import datetime
import json
import hashlib
import hmac
from urllib.parse import urlencode

import requests

from services.exception import RuntimeException


class TransactionException(RuntimeException):
    """Base exception for transaction errors."""
    _title = "Transaction Exception"


class ExchangeClient:
    exchange_name = "bitflyer Lightning"
    
    def get_ticker(self, symbol: str) -> dict:
        """
        Fetches the ticker information for a given symbol.
        :param symbol: The product code for which to fetch the ticker.
        :return: A dictionary containing ticker information.
        """
        path = "/v1/getticker"
        params = {"product_code": symbol}
        response = requests.get(self.base_url + path, params=params)
        return response.json()
    
    def get_health(self, symbol: str) -> dict:
        """
        Fetches the health status of the exchange for a given symbol.
        :param symbol: The product code for which to fetch the health status.
        :return: A dictionary containing health information.
        """
        path = "/v1/getboardstate"
        params = {"product_code": symbol}
        response = requests.get(self.base_url + path, params=params)
        return response.json()
    
    def get_balance(self) -> list:
        """
        Fetches the balance of the account.
        :return: A dictionary containing the account balance.
        """
        path = "/v1/me/getbalance"
        headers = self._get_auth_headers('get', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()
    
    def get_collateral(self) -> dict:
        """
        Fetches the collateral information of the account.
        :return: A dictionary containing the collateral information.
        """
        path = "/v1/me/getcollateral"
        headers = self._get_auth_headers('get', path)
        response = requests.get(self.base_url + path, headers=headers)
        return response.json()
    
    def create_order(self, symbol: str, side: Literal["buy", "sell"], size: float, price: float = None, order_type: str = Literal["limit", "market"]) -> dict:
        """
        Creates a new order.
        :param symbol: The product code for the order.
        :param side: The side of the order, either "buy" or "sell".
        :param size: The size of the order.
        :param price: The price for the order, required for limit orders.
        :param order_type: The type of the order, either "limit" or "market".
        :return: A dictionary containing the order response.
        """
        path = "/v1/me/sendchildorder"
        data = json.dumps({
            "product_code": symbol,
            "child_order_type": order_type.upper(),
            "side": side.upper(),
            "price": price,
            "size": size,
        })
        headers = self._get_auth_headers('post', path, data=data)
        response = requests.post(self.base_url + path, data=data, headers=headers)
        return response.json()
    
    def cancel_order(self, order_id: str = None, child_order_acceptance_id: str = None, symbol: str = None) -> dict:
        """
        Cancels an existing order.
        :param order_id: The ID of the order to cancel.
        :param symbol: The product code for the order, if applicable.
        :return: A dictionary containing the cancellation response.
        """
        path = '/v1/me/cancelchildorder'
        if order_id:
            data = json.dumps({
                "product_code": symbol,
                "order_id": order_id,
            })
        elif child_order_acceptance_id:
            data = json.dumps({
                "product_code": symbol,
                "child_order_acceptance_id": child_order_acceptance_id,
            })
        headers = self._get_auth_headers('post', path, data=data)
        response = requests.post(self.base_url + path, data=data, headers=headers)
        return response.json()
    
    def get_orders(self, symbol: str, order_state: str = None) -> list:
        """
        Fetches all orders or orders for a specific symbol.
        :param symbol: The product code for which to fetch the orders.
        :return: A list of orders.
        """
        path = "/v1/me/getchildorders"
        params = {"product_code": symbol, "child_order_state": order_state}
        headers = self._get_auth_headers('get', path, params=params)
        response = requests.get(self.base_url + path, params=params, headers=headers)
        return response.json()
    
    def get_positions(self, symbol: str) -> dict:
        """
        Fetches the positions for a given symbol.
        :param symbol: The product code for which to fetch positions.
        :return: A dictionary containing position information.
        """
        path = "/v1/me/getpositions"
        params = {"product_code": symbol}
        headers = self._get_auth_headers('get', path, params=params)
        response = requests.get(self.base_url + path, params=params, headers=headers)
        return response.json()
    
    def get_trading_commission(self, symbol: str) -> dict:
        """
        Fetches the trading commission for a given symbol.
        :param symbol: The product code for which to fetch the trading commission.
        :return: A dictionary containing trading commission information.
        """
        path = "/v1/me/gettradingcommission"
        params = {"product_code": symbol}
        headers = self._get_auth_headers('get', path, params=params)
        response = requests.get(self.base_url + path, params=params, headers=headers)
        return response.json()
    
    def _get_auth_headers(self, method: Literal["post", "get"], path: str, params: dict = {}, data: str = '') -> dict:
        """
        Generates authentication headers for API requests.
        :param method: The HTTP method (e.g., 'post', 'get').
        :param path: The API endpoint path.
        :param data: The request body data, if applicable.
        :return: A dictionary containing the authentication headers.
        """
        if params:
            path += f'?{urlencode(params)}'
        timestamp = str(datetime.datetime.today())
        mix = f"{timestamp}{method.upper()}{path}{data}"
        signature = hmac.new(self._api_secret.encode('utf-8'), mix.encode('utf-8'), hashlib.sha256).hexdigest()
        return {
            "ACCESS-KEY": self._api_key,
            "ACCESS-TIMESTAMP": timestamp,
            "ACCESS-SIGN": signature,
            "Content-Type": 'application/json',
        }
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        """
        Initializes the ExchangeClient with API credentials and base URL.
        """
        self.base_url = base_url
        self._api_key = api_key
        self._api_secret = api_secret