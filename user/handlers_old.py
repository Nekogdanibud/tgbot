from aiogram import F, types
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram import Router
from aiogram.fsm.state import State, StatesGroup
from config import Config
from database import get_marzban_username, update_telegram_id
from user.keyboards import (
    get_user_main_menu,
    get_subscription_actions,
    get_apps_keyboard,
    get_back_button
)
import requests
import logging
from utils import get_marzban_token, format_traffic

user_router = Router()
user_router.message.filter(F.from_user.id != Config.ADMIN_ID)

logger = logging.getLogger(__name__)

class UserStates(StatesGroup):
    waiting_transfer_id = State()

@user_router.message(Command("start"))
async def user_start(message: types.Message):
    """Обработчик команды /start, отображает главное меню."""
    await message.answer(
        "👋 Добро пожаловать в VPN сервис!\nВыберите действие:",
        reply_markup=get_user_main_menu()
    )

@user_router.callback_query(F.data == "my_subscription")
async def show_subscription(callback: types.CallbackQuery):
    """Отображает информацию о подписке пользователя."""
    telegram_id = callback.from_user.id
    marzban_username = await get_marzban_username(telegram_id)
    
    if not marzban_username:
        await callback.message.edit_text(
            "У вас нет активной подписки.",
            reply_markup=get_back_button()
        )
        return

    try:
        token = await get_marzban_token()
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(
            f"{Config.MARZBAN_URL}/api/user/{marzban_username}",
            headers=headers
        )
        response.raise_for_status()
        user_data = response.json()

        traffic_used = format_traffic(user_data.get("used_traffic", 0))
        traffic_total = format_traffic(user_data.get("data_limit", 0))
        expiry_date = user_data.get("expire", "Не указано")

        await callback.message.edit_text(
            f"📋 Ваша подписка:\n"
            f"Имя пользователя: {marzban_username}\n"
            f"Использовано трафика: {traffic_used}\n"
            f"Всего трафика: {traffic_total}\n"
            f"Срок действия: {expiry_date}",
            reply_markup=get_subscription_actions()
        )
    except requests.RequestException as e:
        logger.error(f"Ошибка при получении данных подписки: {e}")
        await callback.message.edit_text(
            "Ошибка при получении данных. Попробуйте позже.",
            reply_markup=get_back_button()
        )

@user_router.callback_query(F.data == "download_app")
async def show_apps(callback: types.CallbackQuery):
    """Отображает клавиатуру с приложениями для скачивания."""
    await callback.message.edit_text(
        "Выберите приложение для скачивания:",
        reply_markup=get_apps_keyboard()
    )

@user_router.callback_query(F.data == "setup_guide")
async def setup_guide(callback: types.CallbackQuery):
    """Отправляет инструкцию по настройке VPN."""
    await callback.message.edit_text(
        "📖 Инструкция по настройке VPN:\n"
        "1. Скачайте приложение из раздела 'Скачать приложение'.\n"
        "2. Используйте ваши учетные данные для входа.\n"
        "3. Следуйте инструкциям в приложении.\n"
        "Если возникнут вопросы, обратитесь в поддержку.",
        reply_markup=get_back_button()
    )

@user_router.callback_query(F.data == "transfer_subscription")
async def start_transfer(callback: types.CallbackQuery, state: FSMContext):
    """Запрашивает Telegram ID для переноса подписки."""
    await callback.message.edit_text(
        "Введите Telegram ID пользователя, которому хотите передать подписку:",
        reply_markup=get_back_button()
    )
    await state.set_state(UserStates.waiting_transfer_id)

@user_router.message(UserStates.waiting_transfer_id)
async def process_transfer(message: types.Message, state: FSMContext):
    """Обрабатывает ввод Telegram ID и переносит подписку."""
    new_telegram_id = message.text.strip()
    
    if not new_telegram_id.isdigit():
        await message.answer(
            "Пожалуйста, введите корректный Telegram ID (только цифры).",
            reply_markup=get_back_button()
        )
        return

    telegram_id = message.from_user.id
    marzban_username = await get_marzban_username(telegram_id)

    if not marzban_username:
        await message.answer(
            "У вас нет подписки для переноса.",
            reply_markup=get_back_button()
        )
        await state.clear()
        return

    try:
        await update_telegram_id(marzban_username, int(new_telegram_id))
        await message.answer(
            f"Подписка для {marzban_username} успешно передана пользователю с ID {new_telegram_id}.",
            reply_markup=get_user_main_menu()
        )
    except Exception as e:
        logger.error(f"Ошибка при переносе подписки: {e}")
        await message.answer(
            "Ошибка при переносе подписки. Попробуйте позже.",
            reply_markup=get_back_button()
        )
    finally:
        await state.clear()

@user_router.callback_query(F.data == "how_to_use")
async def how_to_use(callback: types.CallbackQuery):
    """Отправляет инструкцию по использованию сервиса."""
    await callback.message.edit_text(
        "ℹ️ Как использовать VPN сервис:\n"
        "1. Проверьте статус подписки в разделе 'Моя подписка'.\n"
        "2. Скачайте приложение в разделе 'Скачать приложение'.\n"
        "3. Следуйте инструкциям в разделе 'Инструкция по настройке'.\n"
        "4. Для помощи обратитесь в 'Поддержка'.",
        reply_markup=get_back_button()
    )

@user_router.callback_query(F.data == "support")
async def support(callback: types.CallbackQuery):
    """Отправляет контактные данные поддержки."""
    await callback.message.edit_text(
        "📞 Поддержка:\n"
        f"Свяжитесь с нами через @{Config.SUPPORT_USERNAME}",
        reply_markup=get_back_button()
    )

@user_router.callback_query(F.data == "back_to_user_menu")
async def back_to_menu(callback: types.CallbackQuery):
    """Возвращает пользователя в главное меню."""
    await callback.message.edit_text(
        "Главное меню:",
        reply_markup=get_user_main_menu()
    )
