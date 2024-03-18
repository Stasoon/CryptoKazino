from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from src.utils.crypto_bot import create_usdt_invoice, delete_old_checks
from config import IS_ACTION_EVENT_ACTIVE


async def handle_help_cmd(message: Message):
    help_text = (
        '<code>/admin</code> — Меню администратора \n\n'
        
        '<code>/startevent</code> — Начать акцию с x1.1 ставками \n'
        '<code>/addbalance сумма_usdt</code> — Пополнить баланс приложения \n'
        '<code>/deloldchecks</code> — Удалить неиспользованные чеки, которым больше 2 дней \n'
    )
    await message.answer(text=help_text)


async def handle_toggle_action_event(message: Message):
    global IS_ACTION_EVENT_ACTIVE
    IS_ACTION_EVENT_ACTIVE = not IS_ACTION_EVENT_ACTIVE

    if IS_ACTION_EVENT_ACTIVE:
        await message.answer('🎉 Акция активирована!')
    else:
        await message.answer('🛑 Акция остановлена')


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
    router.message.register(handle_help_cmd, Command('help'))

    router.message.register(handle_toggle_action_event, Command('startevent'))

    router.message.register(handle_top_up_crypto_bot_balance, Command('addbalance'))

    router.message.register(handle_delete_old_checks, Command('deloldchecks'))

