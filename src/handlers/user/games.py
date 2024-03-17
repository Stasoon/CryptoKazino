import asyncio
from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Iterable

from aiogram import Bot
from aiogram.enums import DiceEmoji

from config import GAME_CHANNEL_ID, REFERRAL_BONUS_PERCENT
from src.database import checks
from src.database.models import InvoicePayment
from src.database.users import get_user_or_none
from src.keyboards.user import UserKeyboards
from src.messages.user import UserMessages
from src.utils.crypto_bot import make_transfer, create_check, convert_usd_to_rub
from src.utils import logger


async def send_low_balance_notification(bot: Bot, payment: InvoicePayment):
    error_text = (
        f'Кончился баланс в боте‼ \n\n'
        f'{payment.user_id} {payment.username} - {payment.amount_usd}$'
    )
    await bot.send_message(chat_id=GAME_CHANNEL_ID, text=error_text)


class Game(ABC):

    def __init__(self, bot: Bot, payment: InvoicePayment):
        self.bot = bot
        self.payment = payment

    @staticmethod
    @abstractmethod
    def get_options() -> Iterable[str]:
        ...

    @abstractmethod
    async def execute(self, root_message_id: int):
        ...

    async def __send_check(self, amount_usd: float, root_message_id: int, text: str = None):
        bot_username = (await self.bot.get_me()).username
        amount_rub = await convert_usd_to_rub(amount_usd)

        try:
            check = await create_check(amount_usd=amount_usd)
        except Exception:
            if not text:
                text = UserMessages.get_winning_will_be_accrued_by_admin(amount_usd=amount_usd, amount_rub=amount_rub)

            await self.bot.send_message(chat_id=GAME_CHANNEL_ID, text=text, reply_to_message_id=root_message_id)
            return

        checks.create_check(
            check_id=check.check_id, user_id=self.payment.user_id,
            amount_usd=amount_usd, check_type='winning',
            activation_url=check.bot_check_url, user_fullname=self.payment.username
        )

        if not text:
            text = UserMessages.get_winning_accrued(amount_usd=amount_usd, amount_rub=amount_rub)
        await self.bot.send_message(
            chat_id=GAME_CHANNEL_ID, text=text, reply_to_message_id=root_message_id,
            reply_markup=UserKeyboards.get_check_in_bot(bot_username=bot_username, check_id=check.check_id)
        )

    async def accrue_winning(self, amount_usd: float, root_message_id: int):
        try:
            await make_transfer(win_amount_usd=amount_usd, user_id=self.payment.user_id)
        except Exception as e:
            logger.error(f"{e}, {self.payment.__dict__}")
            await self.__send_check(amount_usd, root_message_id)

            if 'NOT_ENOUGH_COINS' in str(e):
                await send_low_balance_notification(bot=self.bot, payment=self.payment)
        else:
            amount_rub = await convert_usd_to_rub(amount_usd)
            text = UserMessages.get_winning_accrued(amount_usd=amount_usd, amount_rub=amount_rub)
            await self.bot.send_message(chat_id=GAME_CHANNEL_ID, text=text, reply_to_message_id=root_message_id)

        # Добавление баланса пригласившему
        user = get_user_or_none(telegram_id=self.payment.user_id)

        if user.referrer_id:
            referrer = get_user_or_none(telegram_id=user.referrer_id)
            if referrer:
                referrer.referral_balance += Decimal(str(amount_usd)) * REFERRAL_BONUS_PERCENT
                referrer.save()


class DiceLessOrGreater(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return 'больше', 'меньше'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DICE, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)
        comment = self.payment.comment.lower()

        if (comment == 'меньше' and dice_msg.dice.value <= 3) or (comment == 'больше' and dice_msg.dice.value >= 4):
            coefficient = Decimal('1.8')
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class DoubleDice(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return '2м', '2б', '2 меньше', '2 больше'

    async def execute(self, root_message_id: int):
        values = []

        for _ in range(2):
            dice_msg = await self.bot.send_dice(
                chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DICE, reply_to_message_id=root_message_id
            )
            values.append(dice_msg.dice.value)
            await asyncio.sleep(0.05)

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)
        comment = self.payment.comment.lower()

        if (
                (comment in ['2м', '2 меньше'] and values[0] <= 3 and values[1] <= 3)
                or
                (comment in ['2б', '2 больше'] and values[0] >= 4 and values[1] >= 4)
        ):
            coefficient = Decimal('2.8')
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class DiceGuessNumber(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return [str(i) for i in range(1, 6+1)]

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DICE, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)

        if self.payment.comment.strip() == dice_msg.dice.value:
            coefficient = Decimal('3')
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class DiceEvenUneven(Game):
    @staticmethod
    def get_options() -> Iterable[str]:
        return 'чет', 'чёт', 'нечет', 'нечёт', 'куб чет', 'куб нечет', 'куб чёт', 'куб нечёт'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DICE, reply_to_message_id=root_message_id
        )
        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)
        comment = self.payment.comment.lower()

        if (
                (comment in ['чет', 'чёт', 'куб нечет', 'куб нечёт'] and dice_msg.dice.value % 2 == 0)
                or
                (comment in ['нечет', 'нечёт', 'куб нечет', 'куб нечёт'] and dice_msg.dice.value % 2 != 0)
        ):
            coefficient = Decimal('1.8')

            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class DicePVP(Game):
    @staticmethod
    def get_options() -> Iterable[str]:
        return 'пвп', 'дуэль'

    async def execute(self, root_message_id: int):
        while True:
            moves = []

            # Отправляем кости
            for i in range(2):
                dice_msg = await self.bot.send_dice(
                    chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DICE, reply_to_message_id=root_message_id
                )
                moves.append(dice_msg.dice.value)
                await asyncio.sleep(0.05)

            dice_animation_seconds = 3
            await asyncio.sleep(dice_animation_seconds)

            # Если значения одинаковые, перезапускаем игру
            if moves[0] == moves[1]:
                await self.bot.send_message(chat_id=GAME_CHANNEL_ID, text=UserMessages.get_tie_restart())
                continue
            # Иначе выдаём выигрыш, если игрок победил
            elif moves[0] > moves[1]:
                coefficient = Decimal('1.8')
                win_amount = coefficient * self.payment.amount_usd
                await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)
                return
            else:
                return


class Football(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return 'фут гол', 'фут мимо', 'футбол гол', 'футбол мимо'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.FOOTBALL, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)

        comment = self.payment.comment.lower()
        coefficient = None

        if comment in ['фут гол', 'футбол гол'] and dice_msg.dice.value in (3, 4, 5):
            coefficient = Decimal('1.3')
        elif comment in ['фут мимо', 'футбол мимо'] and dice_msg.dice.value in (1, 2):
            coefficient = Decimal('1.8')

        if coefficient:
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class Basketball(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return 'баскет гол', 'баскет мимо', 'баскетбол гол', 'баскетбол мимо'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.BASKETBALL, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)

        comment = self.payment.comment.lower()
        coefficient = None

        if comment in ['баскет гол', 'баскетбол гол'] and dice_msg.dice.value in (4, 5):
            coefficient = Decimal('1.8')
        elif comment in ['баскет мимо', 'баскетбол мимо'] and dice_msg.dice.value in (1, 2, 3):
            coefficient = Decimal('1.3')

        if coefficient:
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class Darts(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return 'красное', 'белое', 'мимо', 'центр'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.DART, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)

        coefficient = None
        comment = self.payment.comment.lower()

        if comment == 'красное' and dice_msg.dice.value in (2, 4, 6):
            coefficient = Decimal('1.8')
        elif comment == 'белое' and dice_msg.dice.value in (3, 5):
            coefficient = Decimal('1.8')
        elif comment == 'мимо' and dice_msg.dice.value == 1:  # мимо
            coefficient = Decimal('2.5')
        elif comment == 'центр' and dice_msg.dice.value == 6:  # центр
            coefficient = Decimal('2.5')

        if coefficient:
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)


class Slots(Game):

    @staticmethod
    def get_options() -> Iterable[str]:
        return 'слоты', 'слот'

    async def execute(self, root_message_id: int):
        dice_msg = await self.bot.send_dice(
            chat_id=GAME_CHANNEL_ID, emoji=DiceEmoji.SLOT_MACHINE, reply_to_message_id=root_message_id
        )

        dice_animation_seconds = 3
        await asyncio.sleep(dice_animation_seconds)

        match dice_msg.dice.value:
            case 43:  # lemon x3
                coefficient = Decimal('3.1')
            case 22:  # grape x3
                coefficient = Decimal('4.1')
            case 1 | 65:  # bar x3
                coefficient = Decimal('5.1')
            case 64:  # 7 x3
                coefficient = Decimal('13')
            case _:  # Не выигрышный вариант
                coefficient = None

        if coefficient:
            win_amount = coefficient * self.payment.amount_usd
            await self.accrue_winning(amount_usd=float(win_amount), root_message_id=root_message_id)
