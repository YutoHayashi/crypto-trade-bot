import secrets
import time
import json
import hmac
import hashlib
import asyncio

from websockets import ClientConnection
from websockets.exceptions import ConnectionClosed
from websockets.asyncio.client import connect

from dependency_injector.wiring import inject, Provide

from .logger import Logger
from .handler_dispatcher import HandlerDispatcher


class Stream:
    async def send_auth(self, websocket: ClientConnection):
        timestamp = int(time.time() * 1000)
        nonce = secrets.token_hex(16)
        mix = f"{timestamp}{nonce}"
        sign = hmac.new(self._api_secret.encode(), mix.encode(), hashlib.sha256).hexdigest()
        
        await websocket.send(json.dumps({
            "method": "auth",
            "params": {
                "api_key": self._api_key,
                "timestamp": timestamp,
                "nonce": nonce,
                "signature": sign,
            },
            "id": "auth",
        }).encode(), text=True)
    
    async def send_public_subscriptions(self, websocket: ClientConnection):
        for channel in self.public_channels:
            await websocket.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
                "id": f"subscribe_{channel}",
            }).encode(), text=True)
    
    async def send_private_subscriptions(self, websocket: ClientConnection):
        for channel in self.private_channels:
            await websocket.send(json.dumps({
                "method": "subscribe",
                "params": {
                    "channel": channel,
                },
                "id": f"subscribe_{channel}",
            }).encode(), text=True)
    
    async def receive_message(self, websocket: ClientConnection):
        """
        Receive messages from the WebSocket and dispatch them to the handler dispatcher.
        """
        while True:
            if not self.paused:
                message = await websocket.recv()
                message = json.loads(message)
                
                if 'params' in message and 'message' in message['params'] and 'channel' in message['params']:
                    data = message['params']['message']
                    channel = message['params']['channel']
                    await self.handler_dispatcher.dispatch(data, channel)
                    continue
                
                if 'id' in message and 'result' in message and message['result'] is True:
                    if message['id'] == 'auth':
                        await self.send_private_subscriptions(websocket)
                    self.logger.system.info(f"WebSocket subscription successful for id: {message['id']}")
                    continue
                
                if 'error' in message:
                    self.logger.system.error(f"WebSocket error received (code: {message['error']['code']}): {message['error']['message']}")
            else:
                await asyncio.sleep(1)
    
    async def run(self) -> None:
        """
        Start the WebSocket client.
        This method initializes the WebSocket connection and starts listening for messages.
        """
        self.logger.system.info("Starting WebSocket client...")
        async for websocket in connect(self.url):
            try:
                await asyncio.gather(self.send_auth(websocket),
                                     self.send_public_subscriptions(websocket),
                                     self.receive_message(websocket))
            except ConnectionClosed:
                self.logger.system.info("WebSocket connection closed.")
    
    def pause(self):
        """
        Stop the stream.
        """
        self.paused = True
        self.logger.system.info("The stream is paused.")
    
    def resume(self):
        """
        Resume the stream.
        """
        self.paused = False
        self.logger.system.info("The stream is resumed.")
    
    @inject
    def __init__(self,
                 url: str,
                 api_key: str,
                 api_secret: str,
                 handler_dispatcher: HandlerDispatcher = Provide['handler_dispatcher'],
                 logger: Logger = Provide['logger'],
                 config: dict = Provide['config']):
        """
        Initialize the WebSocket client.
        :param url: The WebSocket URL to connect to.
        :param api_key: The API key for authentication.
        :param api_secret: The API secret for authentication.
        :param handler_dispatcher: The handler dispatcher service to handle incoming messages.
        :param config: The application container configuration dictionary.
        """
        self.url = url
        self._api_key = api_key
        self._api_secret = api_secret
        self.handler_dispatcher = handler_dispatcher
        self.logger = logger
        self.paused = False
        
        crypto_currency_code = config.get('crypto_currency_code')
        self.public_channels = [
            f'lightning_board_snapshot_{crypto_currency_code}',
        ]
        self.private_channels = [
            f'child_order_events',
        ]