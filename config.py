import os
from decimal import Decimal
from typing import Final
from dotenv import load_dotenv, find_dotenv


REFUND_COMMISSION_PERCENT = Decimal('0.09')
REFERRAL_BONUS_PERCENT = Decimal('0.05')
MIN_WITHDRAW_REFERRAL_BALANCE_USD = Decimal('1')

load_dotenv(find_dotenv())

BOT_TOKEN: Final[str] = os.getenv('BOT_TOKEN', 'define me')
OWNER_IDS: Final[tuple] = tuple(int(i) for i in str(os.getenv('BOT_OWNER_IDS')).split(','))

CLIENT_NAME: Final[str] = os.getenv('CLIENT_NAME')
CLIENT_API_ID: Final[int] = int(os.getenv('CLIENT_API_ID'))
CLIENT_API_HASH: Final[str] = os.getenv('CLIENT_API_HASH')

GAME_CHANNEL_ID: Final[int] = int(os.getenv('GAME_CHANNEL_ID'))
RULES_MESSAGE_URL: Final[str] = os.getenv('RULES_MESSAGE_URL')

CRYPTO_BOT_TOKEN: Final[str] = os.getenv('CRYPTO_BOT_TOKEN')
INVOICES_CHAT_ID: Final[int] = int(os.getenv('INVOICES_CHAT_ID'))
INVOICE_URL: Final[str] = os.getenv('INVOICE_URL')
