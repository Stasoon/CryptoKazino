from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from src.keyboards.admin import AdminKeyboards


async def handle_admin_command(message: Message):
    await message.answer('Что вы хотите сделать?', reply_markup=AdminKeyboards.get_admin_menu())


def register_admin_menu_handlers(router: Router):
    router.message.register(handle_admin_command, Command('admin'))
