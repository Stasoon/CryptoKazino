from aiogram import Dispatcher, Router

from .other import register_other_handlers
from .user import register_user_handlers
from .admin import register_admin_handlers
from .errors import register_errors_handler
from ..filters.is_admin_filter import IsAdminFilter
from ..middlewares.user_activity import UserActivityMiddleware


def register_all_handlers(dp: Dispatcher):
    admin_router = Router(name='admin_router')
    admin_router.message.filter(IsAdminFilter())
    admin_router.callback_query.filter(IsAdminFilter())
    register_admin_handlers(router=admin_router)
    register_errors_handler(router=admin_router)

    user_router = Router(name='user_router')
    user_router.message.middleware(UserActivityMiddleware())
    user_router.callback_query.middleware(UserActivityMiddleware())
    register_user_handlers(router=user_router)
    register_errors_handler(router=user_router)

    other_router = Router(name='other_router')
    register_other_handlers(router=other_router)

    dp.include_routers(admin_router, user_router, other_router)
