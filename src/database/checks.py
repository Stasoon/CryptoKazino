from datetime import datetime
from typing import Literal

from peewee import fn

from src.database.models import Check


def create_check(
        check_id: int, amount_usd: float,
        activation_url: str, check_type: Literal['winning', 'refund_error', 'referral'],
        user_fullname: str, user_id: int = None
) -> Check:
    new_check = Check.create(
        check_id=check_id, amount=amount_usd,
        user_id=user_id, user_fullname=user_fullname,
        type=check_type, activation_url=activation_url
    )
    return new_check


def get_check(check_id: int) -> Check | None:
    return Check.get_or_none(Check.check_id == check_id)


def get_checks_sum() -> float:
    total_amount = Check.select(fn.SUM(Check.amount)).scalar()
    return total_amount


def get_user_checks(user_id: int) -> list[Check]:
    return (
        Check
        .select()
        .where(Check.user_id == user_id)
    )



