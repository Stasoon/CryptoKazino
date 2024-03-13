from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.utils.crypto_bot import create_usdt_invoice, delete_old_checks


async def handle_top_up_crypto_bot_balance(message: Message, command: CommandObject):
    if not command.args:
        await message.answer(text='После команды напишите, на сколько USDT хотите пополнить баланс!')
        return

    try:
        amount = float(command.args)
    except ValueError:
        await message.answer('Вы ввели не число!')
        return

    invoice = await create_usdt_invoice(amount=amount)
    await message.answer(f"Пополните счёт по <a href='{invoice.bot_invoice_url}'>ссылке</a>")


async def handle_delete_old_checks(message: Message):
    deleted_checks = await delete_old_checks()
    deleted_checks_text = '\n'.join([str(i) for i in deleted_checks])
    await message.answer(text=f'Чеки удалены: \n\n{deleted_checks_text}')


def register_admin_commands_handlers(router: Router):
    router.message.register(handle_top_up_crypto_bot_balance, Command('addbalance'))

    router.message.register(handle_delete_old_checks, Command('deloldchecks'))

