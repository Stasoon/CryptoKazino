from src import bot, dp
from src.handlers import register_all_handlers
from src.database.models import register_models
from src.utils import logger


async def on_startup():
    # Запуск базы данных
    register_models()

    # Регистрация хэндлеров
    register_all_handlers(dp)

    logger.info('Бот запущен!')


async def on_shutdown():
    logger.info('Бот остановлен')


async def start_bot():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.delete_webhook(drop_pending_updates=False)

    try:
        # Запускаем поллинг
        await dp.start_polling(
            bot, close_bot_session=True,
            allowed_updates=["message", "callback_query", "chat_member", "my_chat_member"]
        )
    except Exception as e:
        logger.exception(e)

