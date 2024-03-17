from datetime import datetime, timedelta

from peewee import fn

from .models import InvoicePayment


def get_payments_usd_sum(hours_back: int = None) -> float:
    query = InvoicePayment.select(fn.SUM(InvoicePayment.amount_usd))

    # Если указано количество часов, ограничиваем выборку платежей по времени
    if hours_back is not None:
        # Вычисляем время, на которое нужно ограничить выборку
        start_time = datetime.now() - timedelta(hours=hours_back)
        # Добавляем условие, что дата платежа должна быть больше или равна start_time
        query = query.where(InvoicePayment.timestamp >= start_time)

    total_amount_usd = query.scalar()
    return total_amount_usd if total_amount_usd else 0

