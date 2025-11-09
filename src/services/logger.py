import os

from logging import Logger, getLogger, DEBUG, INFO, FileHandler, Formatter


class Logger:
    formatter: Formatter = None
    system: Logger = None
    transaction: Logger = None
    
    def __init__(self):
        self.system = getLogger('System')
        self.system.setLevel(DEBUG)
        self.transaction = getLogger('Transaction')
        self.transaction.setLevel(INFO)
        
        self.formatter = Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        system_log_handler = FileHandler(filename=os.environ.get('SYSTEM_LOG_FILENAME'))
        system_log_handler.setFormatter(self.formatter)
        
        transaction_log_handler = FileHandler(filename=os.environ.get('TRANSACTION_LOG_FILENAME'))
        transaction_log_handler.setFormatter(self.formatter)
        
        self.system.addHandler(system_log_handler)
        self.transaction.addHandler(transaction_log_handler)