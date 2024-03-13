import asyncio
from typing import Generator

from aiogram import F, Router, Bot
from aiogram.exceptions import TelegramRetryAfter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardMarkup

from src.database.users import get_user_ids
from src.keyboards.admin import MailingKb
from src.utils import logger


class MailingPostCreating(StatesGroup):
    wait_for_content_message = State()
    wait_for_button_data = State()
    wait_for_confirm = State()


class Messages:
    @staticmethod
    def ask_for_post_content():
        return "Пришлите <u>текст</u> поста, который хотите разослать. Добавьте нужные <u>медиа-файлы</u>"

    @staticmethod
    def get_button_data_incorrect():
        return 'Отправленная информация не верна. ' \
               'Пожалуйста, в первой строке напишите название кнопки, во второй - ссылку.'

    @staticmethod
    def prepare_post():
        return "<i>Пост, который будет разослан:</i>"

    @staticmethod
    def get_mailing_canceled():
        return '⛔ Рассылка отменена'

    @staticmethod
    def get_markup_adding_manual():
        return '''Отправьте боту название кнопки и адрес ссылки. Например, так: \n
Telegram telegram.org \n
Чтобы отправить несколько кнопок за раз, используйте разделитель «|». Каждый новый ряд – с новой строки. Например, так: \n
Telegram telegram.org | Новости telegram.org/blog
FAQ telegram.org/faq | Скачать telegram.org/apps'''

    @staticmethod
    def ask_about_start_mailing():
        return "<u><b>Начать рассылку?</b></u>"

    @staticmethod
    def get_mailing_started():
        return "✅ <b>Рассылка началась!</b>"

    @staticmethod
    def get_successful_mailed(successful_count: int):
        return f'✅ <b>Успешно разослано {successful_count} пользователям.</b>'


class Mailer:
    def __init__(self, bot: Bot, to_user_ids: Generator,
                 message_to_copy_id: int, from_chat_id: int,
                 markup: InlineKeyboardMarkup = None):
        self.bot = bot
        self.user_ids = to_user_ids
        self.message_id = message_to_copy_id
        self.from_chat_id = from_chat_id
        self.markup = markup

    async def _send_message_to_user(self, user_id: int) -> bool:
        try:  # пробуем скопировать сообщение с постом в чат пользователю
            await self.bot.copy_message(user_id, self.from_chat_id, self.message_id, reply_markup=self.markup)
        except TelegramRetryAfter as e:  # обрабатываем ошибку слишком частой отправки
            await asyncio.sleep(e.retry_after)
            return await self._send_message_to_user(user_id)
        except Exception:
            return False
        else:  # возвращаем True, если прошло успешно
            return True

    async def start_mailing(self) -> int:
        successful_count = 0
        try:
            for user_id in self.user_ids:
                if await self._send_message_to_user(user_id):
                    successful_count += 1
                await asyncio.sleep(0.05)
        finally:
            logger.info(f'Рассылка закончилась, {successful_count} юзеров получили сообщения.')
            return successful_count


# Handlers

async def handle_admin_mailing_button(message: Message, state: FSMContext):
    await message.answer(text=Messages.ask_for_post_content(),
                         reply_markup=MailingKb.get_cancel_markup(),
                         parse_mode='HTML')
    await state.set_state(MailingPostCreating.wait_for_content_message)


async def handle_post_content(message: Message, state: FSMContext):
    await state.update_data(message_id=message.message_id)

    await message.answer(text=Messages.get_markup_adding_manual(),
                         reply_markup=MailingKb.get_skip_adding_button_to_post(),
                         disable_web_page_preview=True,
                         parse_mode='HTML')

    await state.set_state(MailingPostCreating.wait_for_button_data)


async def handle_url_button_data(message: Message, state: FSMContext):
    markup = MailingKb.generate_markup_from_text(message.text)

    await message.answer(Messages.prepare_post(), parse_mode='HTML')

    try:
        await message.bot.copy_message(chat_id=message.from_user.id,
                                       message_id=(await state.get_data()).get('message_id'),
                                       from_chat_id=message.from_user.id,
                                       reply_markup=markup)
    except Exception as e:
        print(e)
        await message.answer(
            text='Вы ввели неправильную информацию для кнопок под постом. Попробуйте снова:',
            reply_markup=MailingKb.get_skip_adding_button_to_post()
        )
        return

    await state.update_data(markup=markup)
    await message.answer(Messages.ask_about_start_mailing(),
                         reply_markup=MailingKb.get_confirm_mailing(),
                         parse_mode='HTML')
    await state.set_state(MailingPostCreating.wait_for_confirm)


async def handle_continue_wout_button_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(Messages.prepare_post(), parse_mode='HTML')
    # копируем текущий пост
    await callback.bot.copy_message(
        chat_id=callback.from_user.id,
        from_chat_id=callback.from_user.id,
        message_id=(await state.get_data()).get('message_id')
    )
    # просим подтверждения
    await callback.message.answer(Messages.ask_about_start_mailing(),
                                  reply_markup=MailingKb.get_confirm_mailing(),
                                  parse_mode='HTML')
    await state.set_state(MailingPostCreating.wait_for_confirm)


async def handle_confirm_mailing_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(Messages.get_mailing_started(), parse_mode='HTML')

    data = await state.get_data()
    mailer = Mailer(
        bot=callback.message.bot,
        to_user_ids=get_user_ids(),
        message_to_copy_id=data.get('message_id'),
        from_chat_id=callback.from_user.id,
        markup=data.get('markup')
    )
    successful_count = await mailer.start_mailing()

    await callback.message.answer(text=Messages.get_successful_mailed(successful_count), parse_mode='HTML')
    await state.clear()


async def handle_cancel_mailing_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(Messages.get_mailing_canceled(), parse_mode='HTML')
    await state.clear()


def register_mailing_handlers(router: Router):
    # обработка нажатия на кнопку Рассылки из меню админа
    router.message.register(handle_admin_mailing_button, F.text == '✉ Рассылка')

    # обработка контента поста
    router.message.register(
        handle_post_content,
        F.content_type.in_({'text', 'video', 'photo', 'animation'}),
        MailingPostCreating.wait_for_content_message
    )

    # обработка содержимого для url-кнопки
    router.message.register(
        handle_url_button_data,
        F.content_type == 'text',
        MailingPostCreating.wait_for_button_data
    )

    # обработка калбэка продолжения без url-кнопки
    router.callback_query.register(
        handle_continue_wout_button_callback,
        MailingPostCreating.wait_for_button_data
    )

    # обработка калбэка подтверждения (начала) рассылки
    router.callback_query.register(
        handle_confirm_mailing_callback,
        F.data == 'start_mailing',
        MailingPostCreating.wait_for_confirm
    )

    # обработка отмены рассылки
    router.callback_query.register(handle_cancel_mailing_callback, F.data == 'cancel_mailing')
