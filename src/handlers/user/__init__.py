from aiogram import Router

from .menu import register_menu_handlers
from .start_command import register_start_command_handlers


def register_user_handlers(router: Router):
    register_start_command_handlers(router)
    register_menu_handlers(router)
    # register_invoices_handlers(router)
