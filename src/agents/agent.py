from abc import ABC, abstractmethod

from dependency_injector.wiring import Provide, inject

from services.logger import Logger


class Agent(ABC):
    """
    Abstract base class for agents.
    Agents are responsible for executing tasks and managing their own state.
    """
    
    @abstractmethod
    async def get_action(self, observations: list) -> int:
        """
        Get the action to be taken based on the current state.
        :param observations: The current observations/data.
        :return: The action to be taken.
        """
        pass
    
    @abstractmethod
    async def action(self, action: int) -> None:
        """
        Execute the given action.
        :param action: The action to be executed.
        """
        pass
    
    @inject
    def __init__(self,
                 logger: Logger = Provide['logger'],
                 config: dict = Provide['config']):
        self.logger = logger
        self.crypto_currency_code = config.get('crypto_currency_code')
        self.model_path = config.get('model_path')