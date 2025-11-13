from abc import ABC, abstractmethod

from dependency_injector.wiring import inject, Provide

from services.logger import Logger


class BatchTask(ABC):
    @property
    @abstractmethod
    def interval(self) -> int:
        """
        Get the interval in seconds at which to run the task.
        :return: The interval in seconds.
        """
        return 600  # Default to 10 minutes
    
    @abstractmethod
    async def __call__(self):
        """
        Execute the batch task.
        """
        pass
    
    @inject
    def __init__(self,
                 logger: Logger = Provide['logger'],
                 config: dict = Provide['config']):
        self.logger = logger
        self.legal_currency_code = config.get('legal_currency_code')
        self.crypto_currency_code = config.get('crypto_currency_code')