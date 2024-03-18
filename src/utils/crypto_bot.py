import json
import requests
from decimal import Decimal
from uuid import uuid4
from datetime import datetime, timedelta, timezone

from aiocryptopay import AioCryptoPay, Networks
from aiocryptopay.const import Assets
from aiocryptopay.models.check import Check
from aiocryptopay.models.invoice import Invoice

from config import CRYPTO_BOT_TOKEN, OWNER_IDS
from src.utils import logger


async def make_transfer(win_amount_usd: float, user_id: int):
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)

    error = None
    rate = await get_exchange_rate(source='USDT', target='USD')

    try:
        amount_usdt = Decimal(str(win_amount_usd)) * (Decimal('1') / Decimal(str(rate)))
        await crypto.transfer(
            user_id=user_id, asset=Assets.USDT, amount=float(amount_usdt), spend_id=str(uuid4())[:50]
        )
    except Exception as e:
        error = e

    await crypto.close()

    if error:
        raise error


async def create_usdt_invoice(amount: float) -> Invoice:
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    invoice = await crypto.create_invoice(amount=amount, asset=Assets.USDT, expires_in=3600, allow_anonymous=False)

    await crypto.close()
    return invoice


async def create_check(amount_usd: float) -> Check:
    """ Создаёт чек в USDT """
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)

    try:
        rate = await get_exchange_rate(source='USDT', target='USD')
        amount_usdt = Decimal(str(amount_usd)) * (Decimal('1') / Decimal(str(rate)))
        check = await crypto.create_check(amount=float(amount_usdt), asset=Assets.USDT)
    except Exception as e:
        logger.error(e)
        await crypto.close()
        raise e

    await crypto.close()
    return check


async def get_exchange_rate(source: str, target: str) -> float | None:
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    exchange_rates = await crypto.get_exchange_rates()

    rate = None

    for exchange_rate in exchange_rates:
        if exchange_rate.source == source and exchange_rate.target == target:
            rate = exchange_rate.rate
            break

    await crypto.close()
    return rate


async def convert_usd_to_rub(usd: float) -> float:
    return usd * (1 / await get_exchange_rate(source='RUB', target='USD'))


async def convert_usd_to_usdt(usd: float) -> float:
    return usd * (1 / await get_exchange_rate(source='RUB', target='USD'))


async def delete_old_checks() -> list[int]:
    crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)
    utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)

    checks = (
        c for c in await crypto.get_checks(status='active')
        if utc_now - c.created_at > timedelta(days=2)
    )
    deleted_checks = []

    for check in checks:
        try:
            await crypto.delete_check(check_id=check.check_id)
        except Exception as e:
            pass
        else:
            deleted_checks.append(check.check_id)

    logger.info(f'Удалены чеки: {deleted_checks}')
    await crypto.close()
    return deleted_checks


headers = {
    "Host": "pay.crypt.bot",
    "Crypto-Pay-API-Token": CRYPTO_BOT_TOKEN
}


def get_checks_summ(hours_back: int = None) -> float:
    resp = requests.get(f"https://pay.crypt.bot/api/getChecks", headers=headers)
    checks = json.loads(resp.content).get('result').get('items')

    total_amount = 0

    for check in checks:
        time_filter = True
        if hours_back:
            time = datetime.strptime(check.get('created_at'), '%Y-%m-%dT%H:%M:%S.%fZ')
            time_filter = datetime.now() - time < timedelta(hours=hours_back)

        if check.get('status') == 'activated' and time_filter:
            check_amount = float(check.get('amount'))
            total_amount += check_amount

    return total_amount


def get_transfers_summ(hours_back: int = None) -> float:
    resp = requests.get(f"https://pay.crypt.bot/api/getTransfers", headers=headers)
    transfers = json.loads(resp.content).get('result').get('items')

    total_amount = 0

    for t in transfers:
        time_filter = True
        if hours_back:
            time = datetime.strptime(t.get('completed_at'), '%Y-%m-%dT%H:%M:%S.%fZ')
            time_filter = datetime.now() - time < timedelta(hours=hours_back)

        if t.get('user_id') not in OWNER_IDS and t.get('status') == 'completed' and time_filter:
            total_amount += float(t.get('amount'))

    return total_amount


