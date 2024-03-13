from aiogram import F, Router
from aiogram.enums import ChatType
from aiogram.filters import ChatMemberUpdatedFilter, KICKED, MEMBER
from aiogram.types import ChatMemberUpdated, CallbackQuery, Message

from src.database.users import set_user_blocked_bot, set_user_unblocked_bot


# Блокировка бота
async def handle_bot_blocked(event: ChatMemberUpdated):
    set_user_blocked_bot(user_id=event.from_user.id)


async def handle_bot_unblocked(event: ChatMemberUpdated):
    set_user_unblocked_bot(user_id=event.from_user.id)


# Пустой callback
async def handle_empty_callback(callback: CallbackQuery):
    await callback.answer()


def register_other_handlers(router: Router):
    router.my_chat_member.register(
        handle_bot_blocked,
        F.chat.type == ChatType.PRIVATE,
        ChatMemberUpdatedFilter(member_status_changed=KICKED)
    )

    router.my_chat_member.register(
        handle_bot_unblocked,
        F.chat.type == ChatType.PRIVATE,
        ChatMemberUpdatedFilter(member_status_changed=MEMBER)
    )

    router.callback_query.register(handle_empty_callback, F.data == '*')
