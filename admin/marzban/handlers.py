from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from marzban.api import MarzbanAPI
from .texts import *
from .keyboards import *
import logging

router = Router()
logger = logging.getLogger(__name__)

def safe_divide(value: int, divisor: int, default=0) -> float:
    """Безопасное деление с защитой от None и нуля"""
    if value is None or divisor is None or divisor == 0:
        return default
    return value / divisor

def format_size(bytes_size: int) -> str:
    """Форматирование размера с защитой от None"""
    if bytes_size is None:
        return "∞"
    
    for unit, divisor in [('GB', 1024**3), ('MB', 1024**2), ('KB', 1024)]:
        if bytes_size >= divisor:
            return f"{safe_divide(bytes_size, divisor):.2f} {unit}"
    return f"{bytes_size} B"

@router.callback_query(F.data == "admin:marzban")
async def marzban_main(callback: CallbackQuery):
    await callback.message.edit_text(
        MARZBAN_MENU_TITLE,
        reply_markup=marzban_main_kb()
    )

@router.callback_query(F.data == "marzban:stats")
async def show_stats(callback: CallbackQuery):
    try:
        api = MarzbanAPI()
        stats = api.get_system_stats() or {}
        
        await callback.message.edit_text(
            SERVER_STATS_TITLE + STATS_TEMPLATE.format(
                stats.get('cpu_usage', 'N/A'),
                stats.get('memory_usage', 'N/A'),
                stats.get('total_users', 0),
                stats.get('active_users', 0)
            ),
            reply_markup=marzban_main_kb(),
		parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Stats error: {e}", exc_info=True)
        await callback.answer("Ошибка загрузки статистики")

@router.callback_query(F.data == "marzban:users")
async def first_users_page(callback: CallbackQuery):
    await show_users_page(callback, 0)

@router.callback_query(F.data.startswith("marzban:users:"))
async def specific_users_page(callback: CallbackQuery):
    try:
        page = int(callback.data.split(":")[2])
        await show_users_page(callback, page)
    except (ValueError, IndexError) as e:
        logger.warning(f"Pagination error: {e}")
        await callback.answer("Ошибка пагинации")
        await first_users_page(callback)

async def show_users_page(callback: CallbackQuery, page: int):
    try:
        api = MarzbanAPI()
        users = api.get_users() or []
        
        await callback.message.edit_text(
            USER_LIST_TITLE.format(len(users)),
            reply_markup=users_list_kb(users, page)
        )
    except Exception as e:
        logger.error(f"Users page error: {e}", exc_info=True)
        await callback.answer("Ошибка загрузки списка")

@router.callback_query(F.data.startswith("marzban:user:"))
async def show_user_details(callback: CallbackQuery):
    try:
        username = callback.data.split(":")[2]
        api = MarzbanAPI()
        user = api.get_user(username)
        
        if not user:
            await callback.answer("Пользователь не найден")
            return
        
        await callback.message.edit_text(
            USER_DETAILS_TITLE + USER_DETAILS.format(
                user.get('username', 'N/A'),
                USER_STATUS_ICONS.get(user.get('status'), '⚪'),
                format_size(user.get('data_limit')),
                format_size(user.get('used_traffic')),
                user.get('expire_date', '∞'),
		user.get('sub_last_user_agent', 'Не удалось определить')
            ),
            reply_markup=user_actions_kb(username),
	    parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"User details error: {e}", exc_info=True)
        await callback.answer("Ошибка загрузки данных")
