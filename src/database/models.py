from datetime import datetime

from peewee import (
    Model, PostgresqlDatabase, SqliteDatabase, AutoField,
    SmallIntegerField, BigIntegerField, IntegerField,
    DateTimeField, CharField, DecimalField, BooleanField,
    ForeignKeyField
)


db = SqliteDatabase(
    database='data.db'
    # DatabaseConfig.NAME,
    # user=DatabaseConfig.USER, password=DatabaseConfig.PASSWORD,
    # host=DatabaseConfig.HOST, port=DatabaseConfig.PORT
)


class _BaseModel(Model):
    class Meta:
        database = db


class User(_BaseModel):
    """ Пользователь бота """
    class Meta:
        db_table = 'users'

    telegram_id = BigIntegerField(primary_key=True, unique=True, null=False)
    name = CharField(default='Пользователь')
    username = CharField(null=True, default='Пользователь')

    referrer_id = BigIntegerField(null=True)
    referral_balance = DecimalField(default=0)

    last_activity = DateTimeField(null=True)
    bot_blocked = BooleanField(default=False)
    registration_timestamp = DateTimeField()

    def __str__(self):
        return f"@{self.username}" if self.username else f"tg://user?id={self.telegram_id}"


class InvoicePayment(_BaseModel):
    class Meta:
        db_table = 'payments'

    user_id = BigIntegerField(null=True)
    username = CharField()

    amount = DecimalField()
    currency = CharField()
    amount_usd = DecimalField()

    comment = CharField(max_length=1024)
    timestamp = DateTimeField(default=datetime.now)


class Check(_BaseModel):
    class Meta:
        db_table = 'checks'

    check_id = BigIntegerField()
    amount = DecimalField()
    currency = CharField(default='USDT')

    user_id = BigIntegerField(null=True)
    user_fullname = CharField(null=True)

    activation_url = CharField()
    type = CharField()
    timestamp = DateTimeField(default=datetime.now)


# class Transfer(_BaseModel):
#     class Meta:
#         db_table = 'transfers'
#
#     check_id = BigIntegerField()
#     amount = DecimalField()
#     currency = CharField(default='USDT')
#
#     user_id = BigIntegerField(null=True)
#     user_fullname = CharField(null=True)
#
#     activation_url = CharField()
#     type = CharField()
#     timestamp = DateTimeField(default=datetime.now)


class Admin(_BaseModel):
    """ Администратор бота """
    class Meta:
        db_table = 'admins'

    telegram_id = BigIntegerField(unique=True, null=False)
    name = CharField()


def register_models() -> None:
    for model in _BaseModel.__subclasses__():
        model.create_table()
