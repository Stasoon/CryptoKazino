import re
from decimal import Decimal
from typing import Type

from pyrogram import Client
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.handlers import MessageHandler

from config import INVOICES_CHAT_ID, GAME_CHANNEL_ID, INVOICE_URL, REFUND_COMMISSION_PERCENT
from src.database import checks
from src.database.models import InvoicePayment
from src.handlers.user.games import Game, DiceLessOrGreater, DiceGuessNumber, Basketball, Football, DiceEvenUneven, \
    Darts, Slots, DicePVP, DoubleDice
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.create_bot import bot
from src.utils.crypto_bot import create_check
from src.utils import logger


async def handle_paid_invoice_message(client: Client, message: Message):
    if 'tg://user?id=' in message.text.html:
        pattern = r'<a href="tg://user\?id=(\d+)"><b>(.+)</b></a>.*?([\d\.]+)\s(\w+)\s\(\$([\d\.]+)\)'
        with_id = True
    else:
        pattern = r'<b>(.+)</b>.*?([\d\.]+)\s(\w+)\s\(\$([\d\.]+)\)'
        with_id = False

    matches = re.search(pattern, message.text.html)

    if matches:
        if with_id:
            user_id = int(matches.group(1))
            username = matches.group(2)
            start_group = 2
        else:
            user_id = None
            username = matches.group(1)
            start_group = 1

        amount = Decimal(matches.group(start_group + 1))
        currency = matches.group(start_group + 2)
        amount_usd = Decimal(matches.group(start_group + 3))
        comment = message.text.split('\n')[-1].replace('💬', '', 1).strip()

        payment = InvoicePayment.create(
            user_id=user_id, username=username,
            amount=amount, currency=currency, amount_usd=amount_usd,
            comment=comment, timestamp=message.date
        )
        await __process_payment(payment=payment)
        await client.send_reaction(chat_id=message.chat.id, message_id=message.id, emoji='✍')
    else:
        error_text = 'Не получилось извлечь данные о платеже'
        logger.error(f'{error_text}: \n{message.text.html}')
        await client.send_message(chat_id=message.chat.id, text=error_text, reply_to_message_id=message.id)


async def __process_payment(payment: InvoicePayment):
    comment = payment.comment.lower()
    game_types: list[Type[Game]] = [
        DiceLessOrGreater, DiceGuessNumber, DiceEvenUneven,
        DoubleDice, DicePVP,
        Basketball, Football, Darts, Slots
    ]

    for game_type in game_types:
        if comment in game_type.get_options():
            accept_msg = await bot.send_message(
                chat_id=GAME_CHANNEL_ID, text=UserMessages.get_bet_accepted(payment=payment),
                reply_markup=UserKeyboards.get_make_bet(payment_url=INVOICE_URL)
            )

            game = game_type(payment=payment, bot=bot)
            await game.execute(root_message_id=accept_msg.message_id)

            break
    else:
        await __make_refund(user_id=payment.user_id, user_name=payment.username, amount_usd=payment.amount_usd)


async def __make_refund(amount_usd: Decimal, user_name: str, user_id: int = None):
    refund_amount = amount_usd * (Decimal('1') - REFUND_COMMISSION_PERCENT)

    error_text = UserMessages.get_invalid_command(
        user_name=user_name, commission_percent=int(REFUND_COMMISSION_PERCENT * 100)
    )

    try:
        check = await create_check(amount_usd=float(refund_amount))
    except Exception:
        await bot.send_message(chat_id=GAME_CHANNEL_ID, text=error_text)
        return

    checks.create_check(
        check_id=check.check_id, user_id=user_id, user_fullname=user_name,
        amount_usd=check.amount, check_type='refund_error', activation_url=check.bot_check_url
    )

    bot_username = (await bot.get_me()).username
    markup = UserKeyboards.get_invalid_command_refund(bot_username=bot_username, check_id=check.check_id)
    await bot.send_message(chat_id=GAME_CHANNEL_ID, text=error_text, reply_markup=markup)


async def register_payments_handlers(client: Client):
    crypto_bot_id = 1559501630

    client.add_handler(
        MessageHandler(
            handle_paid_invoice_message,
            (filters.user(users=crypto_bot_id) | filters.user(users=1136918511)) & filters.chat(chats=INVOICES_CHAT_ID)
        )
    )

