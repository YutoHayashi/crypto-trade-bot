from enum import Enum

from dependency_injector.wiring import Provide, inject

from services.exchange_client import ExchangeClient
from services.stream import Stream
from .batch_task import BatchTask


class Health(Enum):
    NORMAL = 'NORMAL'
    BUSY = 'BUSY'
    VERY_BUSY = 'VERY_BUSY'
    SUPER_BUSY = 'SUPER_BUSY'
    NO_ORDER = 'NO_ORDER'
    STOP = 'STOP'


class State(Enum):
    RUNNING = 'RUNNING'
    CLOSED = 'CLOSED'
    STARTING = 'STARTING'
    PREOPEN = 'PREOPEN'
    CIRCUITE_BREAK = 'CIRCUIT_BREAK'


class HealthCheckTask(BatchTask):
    interval: int = 60  # 60 seconds
    
    @inject
    async def __call__(self,
                       exchange_client: ExchangeClient = Provide['exchange_client'],
                       stream: Stream = Provide['stream']):
        """
        Perform a health check.
        This method can be extended to include actual health check logic.
        """
        self.logger.system.info("Performing health check...")
        
        boardstate = exchange_client.get_health(self.crypto_currency_code)
        health = boardstate.get('health', Health.NORMAL.value)
        state = boardstate.get('state', State.RUNNING.value)
        
        if stream.paused and health == Health.NORMAL.value and state == State.RUNNING.value:
            stream.resume()
        elif not stream.paused and (health != Health.NORMAL.value or state != State.RUNNING.value):
            stream.pause()
    
    @inject
    def __init__(self,
                 config: dict = Provide['config']):
        super().__init__()
        self.crypto_currency_code = config.get('crypto_currency_code')