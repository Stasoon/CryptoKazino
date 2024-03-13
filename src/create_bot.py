from aiogram import Dispatcher, Bot
from aiogram.fsm.storage.memory import MemoryStorage
from pyrogram import Client

from config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN, disable_web_page_preview=True, parse_mode='HTML')

storage = MemoryStorage()
dp = Dispatcher(storage=storage)
