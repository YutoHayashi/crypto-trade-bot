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
        return 1
    
    @abstractmethod
    async def __call__(self):
        """
        Execute the batch task.
        """
        pass
    
    @inject
    def __init__(self,
                 logger: Logger = Provide['logger']):
        self.logger = logger