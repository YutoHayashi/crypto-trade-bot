import datetime

from dependency_injector.wiring import inject, Provide

from services.notifier import Notifier
from services.order_book import Order, OrderBook
from .batch_task import BatchTask


class NotificationTask(BatchTask):
    interval: int = 600  # 10 minutes
    
    @inject
    async def __call__(self,
                       notifier: Notifier = Provide['notifier'],
                       order_book: OrderBook = Provide['order_book']):
        """
        Send a notification.
        This method can be extended to include actual notification logic.
        """
        self.logger.system.info("Sending notification...")
        
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = f"Report Order History (~{now})\n\n"
        
        orders = await order_book.get_orders()
        await order_book.flush()
        
        for order in orders:
            message += f"- ID: {order.child_order_acceptance_id}, State: {order.child_order_state}, Price: {order.price}, Size: {order.size}\n"
        if not orders:
            message += "No new orders."
        
        notifier.notify(message)