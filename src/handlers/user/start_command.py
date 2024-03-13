from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from src.database import checks
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.database.users import create_user_if_not_exist, get_user_or_none


async def handle_start_command(message: Message, state: FSMContext):
    await state.clear()

    user = message.from_user
    create_user_if_not_exist(telegram_id=user.id, firstname=user.full_name, username=user.username)

    await message.answer(
        text=UserMessages.get_welcome(user_name=user.first_name),
        reply_markup=UserKeyboards.get_main_menu()
    )


async def handle_get_check_start_command(message: Message, command: CommandObject):
    user = message.from_user
    _, user = create_user_if_not_exist(telegram_id=user.id, firstname=user.full_name, username=user.username)

    check_id = int(command.args.replace('check_', ''))
    check = checks.get_check(check_id=check_id)

    if not check:
        await message.answer('❌ Чек не найден!')
        return

    is_id_correct = bool(check.user_id and check.user_id == message.from_user.id)
    is_name_correct = (not check.user_id) and check.user_fullname == message.from_user.full_name

    if not is_id_correct and not is_name_correct:
        await message.answer(text='❌ Этот чек предназначен для другого пользователя!')
        return

    check.user_id = message.from_user.id
    check.save()

    await message.answer(
        text=f"Заберите чек на <b>{check.amount:.4f}$</b> по <a href='{check.activation_url}'>ссылке</a>",
        reply_markup=UserKeyboards.get_main_menu()
    )


async def handle_referral_link_start_command(message: Message, command: CommandObject, state: FSMContext):
    referrer_id = command.args.replace('ref_', '', 1)
    referrer_id = int(referrer_id) if referrer_id.isdigit() else None

    if not get_user_or_none(telegram_id=referrer_id) or not referrer_id:
        await handle_start_command(message=message, state=state)
        return

    user = message.from_user
    create_user_if_not_exist(
        telegram_id=user.id, firstname=user.first_name, username=user.username, referrer_id=referrer_id
    )
    await handle_start_command(message=message, state=state)


def register_start_command_handlers(router: Router):
    router.message.filter(F.chat.type == ChatType.PRIVATE)

    # Получение чека
    router.message.register(
        handle_get_check_start_command,
        CommandStart(deep_link=True, magic=F.args.startswith('check_')),
    )

    # Переход по реферальной ссылке
    router.message.register(
        handle_referral_link_start_command,
        CommandStart(deep_link=True, magic=F.args.startswith('ref_'))
    )

    # Команда /start
    router.message.register(handle_start_command, CommandStart(deep_link=False))
