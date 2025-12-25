import datetime

from dependency_injector.wiring import inject, Provide

from services.notifier import Notifier
from services.exchange_client import ExchangeClient
from services.order_book import OrderBook
from .batch_task import BatchTask


class NotificationTask(BatchTask):
    interval: int = 600  # 10 minutes
    
    last_collateral_history_id: int = None
    
    @inject
    async def __call__(self,
                       notifier: Notifier = Provide['notifier'],
                       exchange_client: ExchangeClient = Provide['exchange_client'],
                       order_book: OrderBook = Provide['order_book']):
        """
        Send a notification.
        This method can be extended to include actual notification logic.
        """
        self.logger.system.info("Sending notification...")
        
        legal_currency_pnl = 0.0
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Report Order History (~{now})\n\n"
        
        collateral_history = exchange_client.get_collateral_history(after=self.last_collateral_history_id)
        legal_currency_pnl = sum([entry['change'] for entry in collateral_history if entry['currency_code'] == self.legal_currency_code])
        self.last_collateral_history_id = collateral_history[0]['id'] if collateral_history else self.last_collateral_history_id
        
        orders = await order_book.get_orders()
        await order_book.flush()
        
        message += f"PnL: {legal_currency_pnl} {self.legal_currency_code}\n\n"
        
        for order in orders:
            message += f"- ID: {order.child_order_acceptance_id}, State: {order.child_order_state}, Side: {order.side}, Price: {order.price}, Size: {order.size}\n"
        if not orders:
            message += "No new orders."
        
        notifier.notify(message)
    
    @inject
    def __init__(self,
                 exchange_client: ExchangeClient = Provide['exchange_client']):
        super().__init__()
        
        collateral_history = exchange_client.get_collateral_history(count=1)
        if collateral_history:
            self.last_collateral_history_id = collateral_history[0]['id']