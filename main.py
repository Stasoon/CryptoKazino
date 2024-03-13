import asyncio

from src.start_bot import start_bot
from src.start_client import start_client
from src.utils import setup_logger


async def main():
    setup_logger()

    bot_task = asyncio.create_task(start_bot())
    client_task = asyncio.create_task(start_client())

    # Ждем завершения обеих задач
    await asyncio.gather(bot_task, client_task)


asyncio.run(main())
if __name__ == '__main__':
    asyncio.run(main=main())
