from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import Database
from .texts import AdminTexts, AdminButtons
from .keyboards import (
    admin_main_kb,
    moder_kb,
    requests_list_kb,
    request_actions_kb,
    users_list_kb,
    user_actions_kb,
    cancel_kb,
    confirm_broadcast_kb
)

db = Database()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()
    confirmation = State()

class AdminActions:
    async def show_main_menu(self, callback: CallbackQuery, is_admin: bool = True):
        """Главное меню (админ/модератор)"""
        text = AdminTexts.WELCOME if is_admin else AdminTexts.MODER_WELCOME
        kb = admin_main_kb() if is_admin else moder_kb()
        
        try:
            if callback.message.text != text:
                await callback.message.edit_text(
                    text=text,
                    reply_markup=kb
                )
        except:
            await callback.message.answer(
                text=text,
                reply_markup=kb
            )

    async def show_stats(self, callback: CallbackQuery):
        """Показать статистику"""
        stats = await db.get_stats()
        await callback.message.edit_text(
            text=AdminTexts.STATS.format(
                users_count=stats['total_users'],
                active_users=stats['active_staff'],
                requests_count=stats['pending_requests']
            ),
            reply_markup=admin_main_kb() if await self._check_admin(callback.from_user.id) else moder_kb()
        )

    async def show_requests(self, callback: CallbackQuery):
        """Показать список заявок"""
        requests = await db.get_requests()
        if not requests:
            await callback.message.edit_text(
                text="Нет активных заявок",
                reply_markup=admin_main_kb()
            )
            return
            
        await callback.message.edit_text(
            text=AdminTexts.REQUESTS_LIST,
            reply_markup=requests_list_kb(requests)
        )

    async def show_request_detail(self, callback: CallbackQuery, request_id: int):
        """Детали заявки"""
        request = await db.get_request(request_id)
        
        if not request:
            await callback.answer("Заявка не найдена", show_alert=True)
            return
            
        await callback.message.edit_text(
            text=AdminTexts.REQUEST_DETAIL.format(
                id=request_id,
                username=request['username'],
                date=request['processed_at'],
                text=request['text']
            ),
            reply_markup=request_actions_kb(request_id)
        )

    async def approve_request(self, callback: CallbackQuery, request_id: int):
        """Одобрить заявку"""
        await db.approve_request(request_id)
        
        await callback.message.edit_text(
            text=AdminTexts.REQUEST_APPROVED.format(id=request_id),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=AdminButtons.BACK,
                    callback_data="nav:requests"
                )]
            ])
        )

    async def reject_request(self, callback: CallbackQuery, request_id: int):
        """Отклонить заявку"""
        await db.reject_request(request_id)
        
        await callback.message.edit_text(
            text=AdminTexts.REQUEST_REJECTED.format(id=request_id),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text=AdminButtons.BACK,
                    callback_data="nav:requests"
                )]
            ])
        )

    async def show_users(self, callback: CallbackQuery):
        """Показать список пользователей"""
        users_data = await db.get_all_users()
        users = [{
            'id': tg_id,
            'username': username,
            'status': (await db.get_user(tg_id))['status'],
            'is_banned': (await db.get_user(tg_id))['is_banned']
        } for username, tg_id in users_data if await db.get_user(tg_id)]
        
        if not users:
            await callback.message.edit_text(
                text="Нет пользователей",
                reply_markup=admin_main_kb()
            )
            return
            
        await callback.message.edit_text(
            text=AdminTexts.USERS_LIST,
            reply_markup=users_list_kb(users)
        )

    async def show_user_detail(self, callback: CallbackQuery, user_id: int):
        """Детали пользователя"""
        user = await db.get_user(user_id)
        
        if not user:
            await callback.answer("Пользователь не найден", show_alert=True)
            return
            
        await callback.message.edit_text(
            text=AdminTexts.USER_DETAIL.format(
                id=user_id,
                username=user['username'],
                status=user['status'],
                reg_date=user['reg_date']
            ),
            reply_markup=user_actions_kb(user_id, user['is_banned'])
        )

    async def ban_user(self, callback: CallbackQuery, user_id: int):
        """Забанить пользователя"""
        user = await db.get_user(user_id)
        await db.ban_user(user_id, reason="Бан через админ-панель")
        
        await callback.message.edit_text(
            text=AdminTexts.USER_BANNED.format(username=user['username']),
            reply_markup=user_actions_kb(user_id, True)
        )

    async def unban_user(self, callback: CallbackQuery, user_id: int):
        """Разбанить пользователя"""
        user = await db.get_user(user_id)
        await db.unban_user(user_id)
        
        await callback.message.edit_text(
            text=AdminTexts.USER_UNBANNED.format(username=user['username']),
            reply_markup=user_actions_kb(user_id, False)
        )

    async def start_broadcast(self, callback: CallbackQuery, state: FSMContext):
        """Начать рассылку"""
        await callback.message.edit_text(
            text=AdminTexts.BROADCAST_START,
            reply_markup=cancel_kb()
        )
        await state.set_state(BroadcastStates.waiting_for_message)

    async def process_broadcast_message(self, message: Message, state: FSMContext):
        """Обработать текст рассылки"""
        users_count = await db.get_active_users_count()
        await state.update_data(message_text=message.text)
        
        await message.answer(
            text=AdminTexts.BROADCAST_CONFIRM.format(
                text=message.text,
                count=users_count
            ),
            reply_markup=confirm_broadcast_kb()
        )
        await state.set_state(BroadcastStates.confirmation)

    async def confirm_broadcast(self, callback: CallbackQuery, state: FSMContext):
        """Подтвердить рассылку"""
        data = await state.get_data()
        users = await db.get_active_users()
        success = 0
        
        await callback.message.edit_text("⏳ Рассылка начата...")
        
        for user in users:
            try:
                await callback.bot.send_message(
                    chat_id=user['telegram_id'],
                    text=data['message_text']
                )
                success += 1
            except Exception:
                continue
                
        await callback.message.edit_text(
            text=AdminTexts.BROADCAST_SUCCESS.format(
                success=success,
                total=len(users)
            )
        )
        await state.clear()

    async def cancel_broadcast(self, callback: CallbackQuery, state: FSMContext):
        """Отменить рассылку"""
        await callback.message.edit_text(
            text=AdminTexts.BROADCAST_CANCELLED
        )
        await state.clear()

    async def _check_admin(self, user_id: int) -> bool:
        """Проверить права администратора"""
        return await db.is_admin(user_id)

    async def _check_moderator(self, user_id: int) -> bool:
        """Проверить права модератора"""
        return await db.is_moderator(user_id)
