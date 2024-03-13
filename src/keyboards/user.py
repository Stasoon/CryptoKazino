from aiogram.types import InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from src.misc.callbacks_data import BlackJackCallback


def get_check_url(bot_username: str, check_id: int):
    return f'https://t.me/{bot_username}?start=check_{check_id}'


class UserKeyboards:

    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()

        builder.button(text='📊 Статистика')
        builder.button(text='🧾 Мои чеки')
        builder.button(text='💵 Реферальная система')

        builder.adjust(2, 1)
        return builder.as_markup(resize_keyboard=True, persistent=True)

    @staticmethod
    def get_make_bet(payment_url: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='♣ Сделать ставку', url=payment_url)
        return builder.as_markup()

    @staticmethod
    def get_check_in_bot(bot_username: str, check_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🎁 Забрать чек', url=get_check_url(bot_username, check_id))
        return builder.as_markup()

    @staticmethod
    def get_check_by_link(link: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🎁 Забрать чек', url=link)
        return builder.as_markup()

    @staticmethod
    def get_invalid_command_refund(bot_username: str, check_id: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Вернуть средства', url=get_check_url(bot_username, check_id))
        return builder.as_markup()

    @staticmethod
    def get_referral_link(user_id: int, bot_username: str) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        invite_url = (
            f'tg://msg_url?url=https://t.me/{bot_username}?start=ref_{user_id}&text=Присоединяйся%20по%20моей%20ссылке'
        )
        builder.button(text='📲 Отправить приглашение', url=invite_url)
        builder.button(text='💸 Вывести', callback_data='withdraw_ref_balance')

        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def get_blackjack_controls(game_number: int) -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='👇 Взять', callback_data=BlackJackCallback(game_number=game_number, move='take'))
        builder.button(text='✋ Хватит', callback_data=BlackJackCallback(game_number=game_number, move='stand'))
        return builder.as_markup()
