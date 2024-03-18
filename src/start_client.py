from pyrogram import Client, idle

from config import CLIENT_NAME, CLIENT_API_ID, CLIENT_API_HASH
from src.handlers.user.handle_paid_invoices import register_payments_handlers
from src.utils import logger


async def start_client():
    service_client = Client(name=CLIENT_NAME, api_id=CLIENT_API_ID, api_hash=CLIENT_API_HASH)

    # Регистрация хэндлеров
    await register_payments_handlers(service_client)

    logger.info('Запущено')
    await service_client.start()

    await idle()

    await service_client.stop()
