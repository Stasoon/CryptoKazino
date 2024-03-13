# from typing import Union
#
# from aiogram import Bot
# from aiogram.enums import ChatMemberStatus
# from aiogram.exceptions import AiogramError
# from aiogram.filters import BaseFilter
# from aiogram.types import Message, CallbackQuery
#
# from src.utils import logger
#
#
# class IsSubscriberFilter(BaseFilter):
#
#     def __init__(self, should_be_sub: bool = True):
#         self.should_be_sub = should_be_sub
#
#     async def __call__(self, event: Union[Message, CallbackQuery], *args, **kwargs) -> bool:
#         flag = await self.is_user_subscribed(bot=event.bot, user_id=event.from_user.id)
#         return flag == self.should_be_sub
#
#     @staticmethod
#     def get_channels_to_subscribe() -> list[int]:
#         return [CHANNEL_ID]
#
#     @classmethod
#     async def is_user_subscribed(cls, bot: Bot, user_id: int) -> bool:
#         required_roles = [ChatMemberStatus.MEMBER, ChatMemberStatus.CREATOR, ChatMemberStatus.ADMINISTRATOR]
#
#         for chat_id in cls.get_channels_to_subscribe():
#             # Если не получается получить чат - продолжаем
#             try:
#                 chat_member = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
#             except AiogramError as e:
#                 logger.error(e)
#                 continue
#
#             # Если не подписан на один из чатов - возвращаем False
#             if chat_member.status not in required_roles:
#                 return False
#
#         # Если подписан на все, возвращаем True
#         return True
