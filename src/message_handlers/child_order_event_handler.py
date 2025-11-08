import asyncio

from dependency_injector.wiring import inject, Provide

from services.portfolio import Portfolio
from services.order_book import Order, OrderBook
from services.position_book import Position, PositionBook
from services.exchange_client import TransactionException
from .message_handler import MessageHandler


class ChildOrderEventHandler(MessageHandler):
    """
    Handles child order events.
    This handler processes messages related to child orders.
    """
    channel_names = ['child_order_events']
    
    @inject
    async def handle_message(self,
                             data: list|dict,
                             channel: str,
                             order_book: OrderBook = Provide['order_book'],
                             position_book: PositionBook = Provide['position_book'],
                             portfolio: Portfolio = Provide['portfolio']) -> None:
        """
        Handles the incoming message by checking the channel and processing child order data.
        :param data: The data received from the WebSocket message.
        :param channel: The channel from which the message was received.
        :param portfolio: The portfolio service to synchronize the portfolio.
        """
        if 'event_type' in data and data['event_type'] == 'ORDER':
            """Handles order events for child orders.
            This method processes order events and updates the portfolio accordingly."""
            product_code = data['product_code'] if 'product_code' in data else None
            child_order_id = data['child_order_id'] if 'child_order_id' in data else None
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
            child_order_type = data['child_order_type'] if 'child_order_type' in data else None
            expire_date = data['expire_date'] if 'expire_date' in data else None
            side = data['side'] if 'side' in data else None
            price = data['price'] if 'price' in data else None
            size = data['size'] if 'size' in data else None
            
            if (not product_code or not child_order_id or not child_order_acceptance_id or not child_order_type or not expire_date or not side or not price or not size):
                raise TransactionException('Invalid order event data received. Missing required fields: product_code, child_order_id, child_order_acceptance_id, child_order_type, expire_date, side, price, or size.')
            
            _ = await asyncio.gather(
                order_book.add(Order(
                    product_code=product_code,
                    side=side,
                    child_order_type=child_order_type,
                    price=price,
                    size=size,
                    child_order_acceptance_id=child_order_acceptance_id,
                    child_order_id=child_order_id,
                    expire_date=expire_date
                )),
                portfolio.sync()
            )
            
            self.logger.transaction.info(f'Order event received, Order ID: {child_order_acceptance_id}, Side: {size}, Price: {price}, Size: {size}')
        
        elif 'event_type' in data and data['event_type'] == 'EXECUTION':
            """Handles execution events for child orders.
            This method processes execution events and updates the portfolio accordingly."""
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
            side = data['side'] if 'side' in data else None
            price = data['price'] if 'price' in data else None
            size = data['size'] if 'size' in data else None
            
            if child_order_acceptance_id is None or side is None or price is None or size is None:
                raise TransactionException('Invalid execution event data received. Missing required field: child_order_acceptance_id.')
            
            completed, pnl, _ = await asyncio.gather(
                order_book.complete(child_order_acceptance_id),
                position_book.add_and_settle(Position(
                    child_order_acceptance_id=child_order_acceptance_id,
                    side=side,
                    price=price,
                    size=size
                )),
                portfolio.sync()
            )
            
            self.logger.transaction.info(f'Execution event received, Order ID: {child_order_acceptance_id}, PnL: {pnl}')
        
        elif 'event_type' in data and data['event_type'] == 'CANCEL':
            """Handles cancel events for child orders.
            This method processes cancel events and logs the cancellation."""
            child_order_acceptance_id = data['child_order_acceptance_id'] if 'child_order_acceptance_id' in data else None
            
            if child_order_acceptance_id is None:
                raise TransactionException('Invalid cancel event data received. Missing required field: child_order_acceptance_id.')
            
            await order_book.cancel(child_order_acceptance_id)
            
            self.logger.transaction.info(f'Cancel event received, Order ID: {child_order_acceptance_id}')
        
        elif 'event_type' in data and data['event_type'] == 'ORDER_FAILED':
            """Handles order failed events for child orders.
            This method processes order failed events and logs the failure."""
            self.logger.transaction.info('Order failed event received.')
        
        elif 'event_type' in data and data['event_type'] == 'CANCEL_FAILED':
            """Handles cancel failed events for child orders.
            This method processes cancel failed events and logs the failure."""
            self.logger.transaction.info(f'Cancel failed event received, Order ID: {child_order_acceptance_id}')