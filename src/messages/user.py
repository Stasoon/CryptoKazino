import html

from config import RULES_MESSAGE_URL, MIN_WITHDRAW_REFERRAL_BALANCE_USD, REFERRAL_BONUS_PERCENT
from src.database.models import InvoicePayment, Check


class UserMessages:

    @staticmethod
    def get_welcome(user_name: str) -> str:
        return (
            f'<b>Привет, {html.escape(user_name)}!</b>'
        )

    @staticmethod
    def get_bet_accepted(payment: InvoicePayment) -> str:
        return (
            f'<blockquote><b>[✅ Ваша ставка принята]</b></blockquote> \n'
            f'🔑 Игрок: <b>{html.escape(payment.username)}</b> \n'
            f'💵 Сумма ставки: <b>{payment.amount_usd}$</b> \n'
            f'💬 Комментарий: <b>{payment.comment}</b>'
        )

    @staticmethod
    def get_invalid_command(user_name: str, commission_percent: int) -> str:
        return (
            f'<b>❌ Ошибка у игрока {user_name}</b> \n\n'
            
            f'<u>Такая команда не найдена.</u> \n'
            f'Средства будут возвращены c комиссией {commission_percent}% \n\n'
            
            f'<u>Прочитайте закреп и сделайте новую ставку.</u> \n'
            f'<b><a href="{RULES_MESSAGE_URL}">ПРОЧИТАТЬ ЗАКРЕП</a></b>'
        )

    @staticmethod
    def get_winning_accrued(amount_usd: float, amount_rub: float) -> str:
        return (
            f'<b>🎉 Поздравляем, вы выиграли {amount_usd:.2f} USD ({amount_rub:.2f} RUB)!</b> \n\n'

            '<blockquote>🚀 Ваш выигрыш успешно зачислен на ваш CryptoBot кошелёк. \n'
            '🔥 Удачи в следующих ставках!</blockquote>'
        )

    @staticmethod
    def get_winning_will_be_accrued_by_admin(amount_usd: float, amount_rub: float):
        return (
            f'<b>🎉 Поздравляем, вы выиграли <b>{amount_usd:.2f} USD</b> ({amount_rub:.2f} RUB)!</b> \n\n'
            
            '<blockquote>🕦 Ваш выигрыш будет зачислен администраторами вручную. \n'
            '🔥 Удачи в следующих ставках!</blockquote>'
        )

    @staticmethod
    def get_tie_restart() -> str:
        return (
            f'<b>♻ Ничья, начинаю заново...</b>'
        )

    @staticmethod
    def get_referral_system(referrals_count: int, referral_balance: float, user_id: int, bot_username: str) -> str:
        referral_link = f'https://t.me/{bot_username}?start=ref_{user_id}'

        return (
            f'<b>🫂 Наша реферальная система:</b> \n\n'
            
            f'┏🎰 Вы получаете <b>{REFERRAL_BONUS_PERCENT*100}%</b> с выигрышей рефералов. \n'
            f'┗💸 Вывод доступен от <b>{MIN_WITHDRAW_REFERRAL_BALANCE_USD:.2f} $</b> \n\n'
            
            f'┏⚗ Количество рефералов: <b>{referrals_count}</b> \n'
            f'┣💰 Реферальный баланс: <b>{referral_balance:.2f} $</b> \n'
            f'┗🔗 <code>{referral_link}</code>'
        )

    @staticmethod
    def get_checks(user_checks: list[Check]) -> str:
        header_text = '🧾 Ваши чеки: \n\n'

        text = header_text + ' \n'.join([
            f"{n}. Чек на <b>{check.amount:.4f}$</b> — <a href='{check.activation_url}'>ссылка</a>"
            for n, check in enumerate(user_checks, start=1)
        ])
        return text

    @staticmethod
    def get_low_referral_balance(min_amount_for_withdraw: float, user_balance: float):
        return (
            f'❌ Минимальная сумма вывода составляет {min_amount_for_withdraw:.2f}$, '
            f'у тебя есть {user_balance:.2f}$ \n\n'
            
            f'💰 Приглашай людей, чтобы заработать деньги'
        )

    @staticmethod
    def get_referral_withdraw_success(amount_usd: float, amount_rub: float) -> str:
        return (
            f'<b>🎉 Поздравляем, рефералы оставили вам: {amount_usd:.2f} USD ({amount_rub:.2f} RUB)!</b> \n\n'

            '<blockquote>🚀 Ваши честно заработанные будут успешно зачислены на ваш CryptoBot кошелёк. \n'
            '🔥 Удачи в следующих рефералах!</blockquote>'
        )

    @staticmethod
    def get_bot_stats(withdraws_sum: float) -> str:
        return f"💰 <b>Общая сумма выплат: {withdraws_sum:.2f} $</b>"
