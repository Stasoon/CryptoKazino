from aiogram.filters.callback_data import CallbackData
from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


class StatisticCallback(CallbackData, prefix='admin_stats'):
    action: str


class AdminKeyboards:
    @staticmethod
    def get_admin_menu() -> ReplyKeyboardMarkup:
        builder = ReplyKeyboardBuilder()

        builder.button(text='📊 Статистика бота')
        builder.button(text='✉ Рассылка')

        builder.adjust(1)
        return builder.as_markup(resize_keyboard=True)

    # Статистика
    @staticmethod
    def get_statistics() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()

        builder.button(text='Час', callback_data=StatisticCallback(action='hour'))
        builder.button(text='Сутки', callback_data=StatisticCallback(action='day'))
        builder.button(text='Неделя', callback_data=StatisticCallback(action='week'))
        builder.button(text='Месяц', callback_data=StatisticCallback(action='month'))
        builder.button(text='⌨ Другое количество', callback_data=StatisticCallback(action='other'))
        builder.button(text='⏬ Экспорт пользователей ⏬', callback_data=StatisticCallback(action='export'))

        builder.adjust(2, 2, 1, 1)
        return builder.as_markup()

    @staticmethod
    def get_back_from_stats() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='🔙 Назад', callback_data=StatisticCallback(action='back'))
        return builder.as_markup()


class MailingKb:

    @staticmethod
    def get_skip_adding_button_to_post() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='Продолжить без кнопки', callback_data='continue_wout_button')
        return builder.as_markup()

    @staticmethod
    def get_cancel_button() -> InlineKeyboardButton:
        return InlineKeyboardButton(text='🔙 Отменить', callback_data='cancel_mailing')

    @staticmethod
    def get_cancel_markup() -> InlineKeyboardMarkup:
        return InlineKeyboardMarkup(inline_keyboard=[[MailingKb.get_cancel_button()]])

    @staticmethod
    def get_confirm_mailing() -> InlineKeyboardMarkup:
        builder = InlineKeyboardBuilder()
        builder.button(text='❗ Начать рассылку ❗', callback_data='start_mailing')
        builder.add(MailingKb.get_cancel_button())
        builder.adjust(1)
        return builder.as_markup()

    @staticmethod
    def generate_markup_from_text(text: str) -> InlineKeyboardMarkup:
        markup_builder = InlineKeyboardBuilder()

        lines = text.split('\n')  # Получаем строки
        for line in lines:  # итерируемся по строкам
            button_contents = line.strip().split('|')  # разделяем кнопки в строке
            row_builder = InlineKeyboardBuilder()

            for content in button_contents:
                item_parts = content.strip().split()
                text = ' '.join(item_parts[:-1])
                url = item_parts[-1]
                if text and url:
                    row_builder.button(text=text, url=url)

            row_builder.adjust(len(button_contents))
            markup_builder.attach(row_builder)

        return markup_builder.as_markup()

