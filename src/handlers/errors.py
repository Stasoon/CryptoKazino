import traceback

from aiogram import Dispatcher, Router
from aiogram.types import Update
from src.utils import logger


async def handle_errors(update: Update, exception: Exception):
    logger.error(f'Ошибка при обработке запроса {update}: {exception} \n{traceback.format_exc()}')


def register_errors_handler(router: Router | Dispatcher):
    router.error(handle_errors)
