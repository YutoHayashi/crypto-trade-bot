import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

import asyncio

from dotenv import load_dotenv
load_dotenv()

from dependency_injector import containers, providers

import services
import batch_tasks
import message_handlers
import agents


legal_currency_code = 'JPY'
crypto_currency_code = 'FX_BTC_JPY'


class ApplicationContainer(containers.DeclarativeContainer):
    """Dependency Injection Container for the application."""
    config = providers.Configuration()
    
    wiring_config = containers.WiringConfiguration(
        packages=[services, batch_tasks, message_handlers, agents],
        modules=['__main__']
    )
    
    # Services
    exchange_client = providers.Factory(
        services.ExchangeClient,
        base_url=config.bitflyer_api_base_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret
    )
    
    stream = providers.Singleton(
        services.Stream,
        url=config.bitflyer_websocket_url,
        api_key=config.bitflyer_api_key,
        api_secret=config.bitflyer_api_secret
    )
    
    logger = providers.Singleton(services.Logger)
    
    batch = providers.Singleton(
        services.Batch,
        tasks=providers.List(
            providers.Factory(batch_tasks.HealthCheckTask),
            providers.Factory(batch_tasks.NotificationTask),
        ),
    )
    
    notifier = providers.Singleton(
        services.Notifier,
        line_messaging_api_base_url=config.line_messaging_api_base_url,
        line_messaging_api_channel_token=config.line_messaging_api_channel_token,
        line_messaging_api_destination_user_id=config.line_messaging_api_destination_user_id
    )
    
    s3client = providers.Singleton(
        services.S3Client,
        bucket=config.s3_bucket
    )
    
    portfolio = providers.Singleton(services.Portfolio)
    
    order_book = providers.Singleton(services.OrderBook)
    
    position_book = providers.Singleton(services.PositionBook)
    
    data_store = providers.Singleton(
        services.DataStore,
        max_size=config.data_store_size
    )
    
    handler_dispatcher = providers.Singleton(
        services.HandlerDispatcher,
        handlers=providers.List(
            providers.Factory(message_handlers.BoardEventHandler),
            providers.Factory(message_handlers.ChildOrderEventHandler)
        )
    )
    
    agent = providers.Singleton(agents.RandomAgent)


async def bot(container: ApplicationContainer) -> None:
    """
    Main entry point for the bot application.
    This function initializes the application container, synchronizes the portfolio,
    and starts the stream.
    :param container: The application container that holds all services and configurations.
    """
    await asyncio.gather(
        container.portfolio().sync(),
        container.order_book().sync(),
        container.position_book().sync()
    )
    await asyncio.gather(
        container.batch().run(),
        container.stream().run()
    )


def main() -> None:
    """Main function to set up and run the bot application."""
    
    container = ApplicationContainer()
    
    container.config.from_dict({
        'legal_currency_code': legal_currency_code,
        'crypto_currency_code': crypto_currency_code,
        'data_store_size': 120,
    })
    
    container.config.bitflyer_websocket_url.from_env('BITFLYER_WEBSOCKET_URL')
    container.config.bitflyer_api_base_url.from_env('BITFLYER_API_BASE_URL')
    container.config.bitflyer_api_key.from_env('BITFLYER_API_KEY')
    container.config.bitflyer_api_secret.from_env('BITFLYER_API_SECRET')
    container.config.s3_bucket.from_env('S3_BUCKET')
    container.config.line_messaging_api_base_url.from_env('LINE_MESSAGING_API_BASE_URL')
    container.config.line_messaging_api_channel_token.from_env('LINE_MESSAGING_API_CHANNEL_TOKEN')
    container.config.line_messaging_api_destination_user_id.from_env('LINE_MESSAGING_API_DESTINATION_USER_ID')
    container.config.model_path.from_env('MODEL_PATH')
    
    container.wire()
    
    asyncio.run(bot(container))


if __name__ == '__main__':
    main()