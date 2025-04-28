from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
import aiohttp
import logging
from datetime import datetime

from config import Config
from database import get_marzban_username, update_telegram_id
from user.keyboards import (
    get_user_main_menu,
    get_subscription_actions,
    get_apps_keyboard,
    get_back_button
)
from user.texts import UserTexts
from utils import get_marzban_token, format_traffic

# Инициализация роутера
user_router = Router()
logger = logging.getLogger(__name__)

class UserStates(StatesGroup):
    waiting_transfer_id = State()

def format_expiry_date(expire_timestamp: int) -> str:
    """Форматирование даты окончания подписки"""
    return (datetime.fromtimestamp(expire_timestamp).strftime("%d.%m.%Y %H:%M") 
            if expire_timestamp else "Бессрочно")

@user_router.message(Command("start"))
async def user_start(message: types.Message):
    """Обработчик команды /start"""
    await message.answer(UserTexts.START, reply_markup=get_user_main_menu())

async def _get_user_data(marzban_username: str):
    """Получение данных пользователя из Marzban"""
    token = await get_marzban_token()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f"{Config.MARZBAN_URL}/api/user/{marzban_username}",
            headers={"Authorization": f"Bearer {token}"}
        ) as response:
            return await response.json() if response.status == 200 else None

@user_router.callback_query(F.data == "my_subscription")
async def show_subscription(callback: types.CallbackQuery):
    """Информация о подписке"""
    try:
        if not (marzban_username := await get_marzban_username(callback.from_user.id)):
            return await callback.message.edit_text(
                UserTexts.NO_SUBSCRIPTION,
                reply_markup=get_back_button()
            )

        if user_data := await _get_user_data(marzban_username):
            await callback.message.edit_text(
                UserTexts.subscription_info(
                    username=marzban_username,
                    used=format_traffic(user_data.get("used_traffic", 0)),
                    total=format_traffic(user_data.get("data_limit", 0)),
                    expire=format_expiry_date(user_data.get("expire"))
                ),
                reply_markup=get_subscription_actions(),
                parse_mode="HTML"
            )
        else:
            await callback.message.edit_text(
                UserTexts.SUBSCRIPTION_ERROR,
                reply_markup=get_back_button()
            )
    except Exception as e:
        logger.error(f"Subscription error: {e}", exc_info=True)
        await callback.message.edit_text(
            UserTexts.SUBSCRIPTION_ERROR,
            reply_markup=get_back_button()
        )

@user_router.callback_query(F.data.in_({"download_app", "setup_guide", "how_to_use"}))
async def handle_info_commands(callback: types.CallbackQuery):
    """Обработчик информационных команд"""
    text = {
        "download_app": UserTexts.APPS_MENU,
        "setup_guide": UserTexts.SETUP_GUIDE,
        "how_to_use": UserTexts.HOW_TO_USE
    }[callback.data]
    
    reply_markup = (
        get_apps_keyboard() 
        if callback.data == "download_app" 
        else get_back_button()
    )
    
    await callback.message.edit_text(text, reply_markup=reply_markup)

@user_router.callback_query(F.data == "transfer_subscription")
async def start_transfer(callback: types.CallbackQuery, state: FSMContext):
    """Начало переноса подписки"""
    await callback.message.edit_text(
        UserTexts.TRANSFER_REQUEST,
        reply_markup=get_back_button()
    )
    await state.set_state(UserStates.waiting_transfer_id)

@user_router.message(UserStates.waiting_transfer_id)
async def process_transfer(message: types.Message, state: FSMContext):
    """Обработка переноса подписки"""
    try:
        if not message.text.strip().isdigit():
            return await message.answer(
                UserTexts.INVALID_TRANSFER_ID,
                reply_markup=get_back_button()
            )

        if not (marzban_username := await get_marzban_username(message.from_user.id)):
            return await message.answer(
                UserTexts.NO_SUBSCRIPTION_TO_TRANSFER,
                reply_markup=get_back_button()
            )

        await update_telegram_id(marzban_username, int(message.text))
        await message.answer(
            UserTexts.TRANSFER_SUCCESS.format(
                username=marzban_username,
                new_id=message.text
            ),
            reply_markup=get_user_main_menu()
        )
    except Exception as e:
        logger.error(f"Transfer error: {e}", exc_info=True)
        await message.answer(
            UserTexts.TRANSFER_ERROR,
            reply_markup=get_back_button()
        )
    finally:
        await state.clear()

@user_router.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    """Поддержка"""
    await callback.message.edit_text(
        UserTexts.support(Config.SUPPORT_USERNAME),
        reply_markup=get_back_button()
    )

@user_router.callback_query(F.data == "back_to_user_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Возврат в главное меню"""
    await callback.message.edit_text(
        UserTexts.MAIN_MENU,
        reply_markup=get_user_main_menu()
    )
