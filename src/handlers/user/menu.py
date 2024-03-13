from aiogram import Router, F
from aiogram.enums import ChatType
from aiogram.types import Message, CallbackQuery

from config import MIN_WITHDRAW_REFERRAL_BALANCE_USD
from src.database import checks
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.database.users import get_user_or_none, get_user_referrals_count
from src.utils import logger
from src.utils.crypto_bot import create_check, convert_usd_to_rub


async def handle_my_checks_button_message(message: Message):
    user_checks = checks.get_user_checks(user_id=message.from_user.id)

    if not user_checks:
        await message.answer('У вас нет активных чеков!')
        return

    text = UserMessages.get_checks(user_checks=user_checks)
    await message.answer(text)


async def handle_statistics_button_message(message: Message):
    stats_text = UserMessages.get_bot_stats(checks.get_checks_sum() + 1132)
    await message.answer(text=stats_text)


async def handle_referral_system_button_message(message: Message):
    bot_username = (await message.bot.get_me()).username
    user = get_user_or_none(telegram_id=message.from_user.id)
    refs_count = get_user_referrals_count(telegram_id=message.from_user.id)

    text = UserMessages.get_referral_system(
        referrals_count=refs_count, referral_balance=user.referral_balance,
        user_id=message.from_user.id, bot_username=bot_username,
    )
    markup = UserKeyboards.get_referral_link(user_id=message.from_user.id, bot_username=bot_username)

    await message.answer(text=text, reply_markup=markup)


async def handle_withdraw_referral_balance_callback(callback: CallbackQuery):
    user = get_user_or_none(telegram_id=callback.from_user.id)

    if user.referral_balance < MIN_WITHDRAW_REFERRAL_BALANCE_USD:
        error_text = UserMessages.get_low_referral_balance(
            min_amount_for_withdraw=MIN_WITHDRAW_REFERRAL_BALANCE_USD,
            user_balance=user.referral_balance
        )
        await callback.answer(text=error_text, show_alert=True)

        return

    try:
        check = await create_check(amount_usd=float(user.referral_balance))
    except Exception as e:
        logger.error(e)
        await callback.answer(text='Произошла ошибка! \n\n🕔Попробуйте снова через некоторое время', show_alert=True)
        return

    checks.create_check(
        check_id=check.check_id, amount_usd=check.amount, activation_url=check.bot_check_url,
        check_type='referral', user_fullname=user.name, user_id=callback.from_user.id
    )
    user.referral_balance = 0
    user.save()

    amount_rub = await convert_usd_to_rub(usd=check.amount)
    congrats_text = UserMessages.get_referral_withdraw_success(amount_usd=check.amount, amount_rub=amount_rub)
    markup = UserKeyboards.get_check_by_link(check.bot_check_url)

    await callback.message.answer(congrats_text, reply_markup=markup)
    await callback.message.delete()


######
async def f(msg):
    if msg.dice:
        print(msg.dice.value)
    if msg.text:
        print(msg.html_text)


def register_menu_handlers(router: Router):
    router.message.filter(F.chat.type == ChatType.PRIVATE)
    router.callback_query.filter(F.message.chat.type == ChatType.PRIVATE)

    # Мои чеки
    router.message.register(handle_my_checks_button_message, F.text.lower().contains('мои чеки'))

    # Статистика
    router.message.register(handle_statistics_button_message, F.text.lower().contains('статистика'))

    # Реферальная система
    router.message.register(handle_referral_system_button_message, F.text.lower().contains('реферальная система'))

    # Реферальная система
    router.callback_query.register(handle_withdraw_referral_balance_callback, F.data == 'withdraw_ref_balance')

    ##########
    router.message.register(f)
