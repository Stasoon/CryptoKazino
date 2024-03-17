import os
import csv
from datetime import datetime
from tempfile import NamedTemporaryFile

from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile

from src.database import users
from src.database.payments import get_payments_usd_sum
from src.database.users import get_all_users
from src.keyboards.admin import AdminKeyboards, StatisticCallback
from src.utils import crypto_bot


# region Utils

class Utils:
    @staticmethod
    def __get_users_csv_filename() -> str:
        csv_folder = 'users_export'

        if not os.path.exists(csv_folder):
            os.mkdir(csv_folder)

        date = datetime.now().strftime("%Y.%m.%d")
        file_name = f"{csv_folder}/Пользователи {date}.csv"

        if os.path.exists(file_name):
            os.remove(file_name)
        return file_name

    @staticmethod
    def write_users_to_xl() -> str:
        file_name = Utils.__get_users_csv_filename()

        with open(file_name, 'w', newline='', encoding='utf-8-sig') as csv_file:
            fieldnames = [
                'telegram_id', 'Имя', 'Юзернейм', 'Время регистрации'
            ]
            writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
            writer.writeheader()

            # Запишите каждую запись из таблицы в CSV файл
            for user in get_all_users():
                writer.writerow({
                    'telegram_id': user.telegram_id,
                    'Имя': user.name,
                    'Юзернейм': user.username,
                    'Время регистрации': user.registration_timestamp,
                })

        return file_name

    @staticmethod
    def write_user_ids_to_txt() -> str:
        with NamedTemporaryFile(delete=False) as temp_file:
            # Записываем данные во временный файл
            for user in get_all_users():
                temp_file.write(f"{user.telegram_id}\n".encode('utf-8'))

            # Получаем имя временного файла
            temp_file_path = temp_file.name
        return temp_file_path


class Messages:
    @staticmethod
    def get_statistic_info(key: str) -> str:
        return {
            'all_time': f'Всего пользовалось ботом: <b>{users.get_users_total_count()} юзеров</b>',
            'month': Messages.get_count_per_hours('месяц', 30 * 24),
            'week': Messages.get_count_per_hours('неделю', 7 * 24),
            'day': Messages.get_count_per_hours('сутки', 24),
            'hour': Messages.get_count_per_hours('час', 1),
            'other': '🔘 Введите количество часов, за которое хотите получить статистику: ',
        }.get(key)

    @staticmethod
    def get_menu():
        users_total_count = users.get_users_total_count()
        blocked_users_count = users.get_blocked_users_count()
        text = (
            f'📊 Статистика \n\n'
            f'👥 Всего в базе: {users_total_count} \n'
            f'🌐 Онлайн: {users.get_online_users_count()} \n'
            f'🚫 Блокировали бота: {blocked_users_count} \n'
            f'🟢 Живых: {users_total_count - blocked_users_count}\n'
        )
        return text + f' \n📊 Выберите, за какой промежуток времени просмотреть статистику:'

    @staticmethod
    def get_count_per_hours(time_word: str, hours: int):
        c = crypto_bot.get_checks_summ(hours_back=hours)
        t = crypto_bot.get_transfers_summ(hours_back=hours)
        p = get_payments_usd_sum(hours_back=hours)
        return (
            f'За {time_word} в бота пришли: \n'
            f'<b>{users.get_users_registered_within_hours_count(hours)} юзера(ов)</b> \n\n'
            f'Чеки: {c} USDT \n'
            f'Переводы: {t} USDT \n'
            f'Ставки: {p} $ \n'
            f'Доход: {p - c - t} $'
        )


class StatsGettingStates(StatesGroup):
    wait_for_hours_count = State()

# endregion


# region Handlers

async def handle_admin_statistic_button(message: Message):
    await message.answer(text=Messages.get_menu(), reply_markup=AdminKeyboards.get_statistics())


async def handle_show_stats_callback(callback: CallbackQuery, state: FSMContext, callback_data: StatisticCallback):
    message = callback.message

    if callback_data.action == 'back':
        await message.edit_text(text=Messages.get_menu(), reply_markup=AdminKeyboards.get_statistics())
        await state.clear()
        return

    response = Messages.get_statistic_info(callback_data.action)
    if response:
        await message.edit_text(text=response, reply_markup=AdminKeyboards.get_back_from_stats())

    if callback_data.action == 'other':
        await state.set_state(StatsGettingStates.wait_for_hours_count)


async def handle_get_hours_message(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer(
            text='❗Вы ввели не число. Попробуйте снова:',
            reply_markup=AdminKeyboards.get_back_from_stats()
        )
        return

    users_count = users.get_users_registered_within_hours_count(int(message.text))
    await message.answer(
        text=Messages.get_count_per_hours(f'{message.text} часов', users_count),
        reply_markup=AdminKeyboards.get_back_from_stats()
    )
    await state.clear()


async def handle_export_callback(callback: CallbackQuery):
    file_name = Utils.write_users_to_xl()
    await callback.message.answer_document(document=FSInputFile(path=file_name))

    # Отправляем временный файл как документ
    txt_temp_file_path = Utils.write_user_ids_to_txt()
    await callback.message.answer_document(document=FSInputFile(path=txt_temp_file_path, filename='user_ids.txt'))
    os.remove(txt_temp_file_path)
    await callback.answer()


# endregion


def register_admin_statistic_handlers(router: Router):
    # Переход из меню
    router.message.register(handle_admin_statistic_button, F.text == '📊 Статистика бота')

    # Кнопка экспорт
    router.callback_query.register(handle_export_callback, StatisticCallback.filter(F.action == 'export'))

    # Показать статистику за период
    router.callback_query.register(handle_show_stats_callback, StatisticCallback.filter())

    # Ввод количества часов для показа статистики
    router.message.register(handle_get_hours_message, StatsGettingStates.wait_for_hours_count)
