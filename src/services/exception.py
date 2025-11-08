from dependency_injector.wiring import inject, Provide

from .logger import Logger


class BaseException(Exception):
    """Base exception for all custom exceptions."""
    _title = "Exception"
    
    @inject
    def __init__(self,
                 message: str = 'An error occurred',
                 logger: Logger = Provide['logger']):
        super().__init__(message)
        self.message = f"{self._title} - {message}"
        logger.system.error(self.message)
    
    def __str__(self):
        return f"{self.__class__.__name__}: {self.message}"
    
    def __repr__(self):
        return f"{self.__class__.__name__}('{self.message}')"


class LogicException(BaseException):
    """Logic exception."""
    _title = "Logic Exception"


class RuntimeException(BaseException):
    """Runtime exception."""
    _title = "Runtime Exception"