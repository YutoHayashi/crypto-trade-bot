from dependency_injector.wiring import inject, Provide

from services.data_store import DataStore
from agents import Agent
from .message_handler import MessageHandler


class BoardEventHandler(MessageHandler):
    """
    Handles board events for a specific cryptocurrency.
    This handler processes messages related to the lightning board snapshot for the specified cryptocurrency.
    """
    channel_names = []
    
    @inject
    async def handle_message(self,
                             data: list|dict,
                             channel: str,
                             agent: Agent = Provide['agent'],
                             data_store: DataStore = Provide['data_store']) -> None:
        """
        Handles the incoming message by checking the channel and appending data to the buffer if it matches.
        :param data: The data received from the WebSocket message.
        :param channel: The channel from which the message was received.
        :param data_store: The data store service to append data to.
        :param portfolio: The portfolio service (not used in this handler but can be extended).
        """
        data_store.append(data)
        
        if (len(data_store) == data_store.max_size):
            action = agent.get_action(data_store.get_data())
            agent.action(action)
    
    def __init__(self):
        """
        Initializes the BoardEventHandler with the cryptocurrency code.
        """
        super().__init__()
        self.channel_names.append(f'lightning_board_snapshot_{self.crypto_currency_code}')