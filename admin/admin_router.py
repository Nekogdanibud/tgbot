from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from database import Database
from admin.admin_actions import AdminActions, BroadcastStates
from admin.keyboards import (
    admin_main_kb,
    moder_kb,
    requests_list_kb,
    request_actions_kb,
    users_list_kb,
    user_actions_kb,
    cancel_kb,
    confirm_broadcast_kb
)
from admin.texts import AdminTexts

admin_router = Router()
db = Database()
actions = AdminActions()

def check_access(callback: CallbackQuery) -> bool:
    """Проверка прав доступа для callback"""
    return db.is_admin(callback.from_user.id) or db.is_moderator(callback.from_user.id)

# ================== Основные команды ==================
@admin_router.message(Command("admin"))
async def admin_start(message: Message):
    if await db.is_admin(message.from_user.id):
        await message.answer(
            text=AdminTexts.WELCOME,
            reply_markup=admin_main_kb()
        )

@admin_router.message(Command("moder"))
async def moder_start(message: Message):
    if await db.is_moderator(message.from_user.id):
        await message.answer(
            text=AdminTexts.MODER_WELCOME,
            reply_markup=moder_kb()
        )

# ================== Навигация ==================
@admin_router.callback_query(F.data == "nav:main")
async def main_menu(callback: CallbackQuery):
    if not await check_access(callback):
        return await callback.answer(AdminTexts.ACCESS_DENIED, show_alert=True)
    
    is_admin = await db.is_admin(callback.from_user.id)
    await actions.show_main_menu(callback, is_admin)

@admin_router.callback_query(F.data == "nav:cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await main_menu(callback)

# ================== Заявки ==================
@admin_router.callback_query(F.data.startswith("nav:requests"))
async def handle_requests(callback: CallbackQuery):
    if not await check_access(callback):
        return await callback.answer(AdminTexts.ACCESS_DENIED, show_alert=True)
    
    # Обработка пагинации
    if ":page:" in callback.data:
        offset = int(callback.data.split(":")[-1])
        requests = await db.get_requests()
        await callback.message.edit_text(
            text=AdminTexts.REQUESTS_LIST,
            reply_markup=requests_list_kb(requests, offset)
        )
        return
    
    # Детали заявки
    if ":detail:" in callback.data:
        request_id = int(callback.data.split(":")[-1])
        await actions.show_request_detail(callback, request_id)
        return
    
    # Основной список заявок
    requests = await db.get_requests()
    await callback.message.edit_text(
        text=AdminTexts.REQUESTS_LIST,
        reply_markup=requests_list_kb(requests)
    )

@admin_router.callback_query(F.data.startswith("action:requests:"))
async def handle_request_actions(callback: CallbackQuery):
    action = callback.data.split(":")[2]
    request_id = int(callback.data.split(":")[-1])
    
    if action == "approve":
        await actions.approve_request(callback, request_id)
    elif action == "reject":
        await actions.reject_request(callback, request_id)

# ================== Пользователи ==================
@admin_router.callback_query(F.data.startswith("nav:users"))
async def handle_users(callback: CallbackQuery):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer(AdminTexts.ACCESS_DENIED, show_alert=True)
    
    # Обработка пагинации
    if ":page:" in callback.data:
        offset = int(callback.data.split(":")[-1])
        users_data = await db.get_all_users()
        users = [{
            'id': tg_id,
            'username': username,
            'status': (await db.get_user(tg_id))['status'],
            'is_banned': (await db.get_user(tg_id))['is_banned']
        } for username, tg_id in users_data if await db.get_user(tg_id)]
        
        await callback.message.edit_text(
            text=AdminTexts.USERS_LIST,
            reply_markup=users_list_kb(users, offset)
        )
        return
    
    # Детали пользователя
    if ":detail:" in callback.data:
        user_id = int(callback.data.split(":")[-1])
        await actions.show_user_detail(callback, user_id)
        return
    
    # Основной список пользователей
    users_data = await db.get_all_users()
    users = [{
        'id': tg_id,
        'username': username,
        'status': (await db.get_user(tg_id))['status'],
        'is_banned': (await db.get_user(tg_id))['is_banned']
    } for username, tg_id in users_data if await db.get_user(tg_id)]
    
    await callback.message.edit_text(
        text=AdminTexts.USERS_LIST,
        reply_markup=users_list_kb(users)
    )

@admin_router.callback_query(F.data.startswith("action:users:"))
async def handle_user_actions(callback: CallbackQuery):
    action = callback.data.split(":")[2]
    user_id = int(callback.data.split(":")[-1])
    
    if action == "ban":
        await actions.ban_user(callback, user_id)
    elif action == "unban":
        await actions.unban_user(callback, user_id)

# ================== Статистика ==================
@admin_router.callback_query(F.data == "nav:stats")
async def show_stats(callback: CallbackQuery):
    await actions.show_stats(callback)

# ================== Рассылка ==================
@admin_router.callback_query(F.data == "nav:broadcast")
async def start_broadcast(callback: CallbackQuery, state: FSMContext):
    if not await db.is_admin(callback.from_user.id):
        return await callback.answer(AdminTexts.ACCESS_DENIED, show_alert=True)
    
    await actions.start_broadcast(callback, state)

@admin_router.message(BroadcastStates.waiting_for_message)
async def process_broadcast_message(message: Message, state: FSMContext):
    if not await db.is_admin(message.from_user.id):
        return
    
    await actions.process_broadcast_message(message, state)

@admin_router.callback_query(
    F.data == "action:broadcast:confirm",
    StateFilter(BroadcastStates.confirmation)
)
async def confirm_broadcast(callback: CallbackQuery, state: FSMContext):
    await actions.confirm_broadcast(callback, state)
