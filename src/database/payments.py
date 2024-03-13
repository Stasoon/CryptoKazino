from peewee import fn

from .models import InvoicePayment


def get_payments_usd_sum() -> float:
    total_amount_usd = InvoicePayment.select(fn.SUM(InvoicePayment.amount_usd)).scalar()
    return total_amount_usd
