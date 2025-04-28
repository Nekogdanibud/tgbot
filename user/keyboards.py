from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Optional

def get_user_main_menu() -> InlineKeyboardMarkup:
    """Главное меню пользователя"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Одна кнопка в первом ряду
            [InlineKeyboardButton(text="📡 Моя подписка", callback_data="my_subscription")],
            
            # Две кнопки во втором ряду
            [
                InlineKeyboardButton(text="❓ Как пользоваться", callback_data="how_to_use"),
                InlineKeyboardButton(text="🆘 Поддержка", callback_data="support")
            ]
        ]
    )

def get_subscription_actions() -> InlineKeyboardMarkup:
    """Действия с подпиской"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Две кнопки в первом ряду
            [
                InlineKeyboardButton(text="📲 Скачать приложение", callback_data="download_app"),
                InlineKeyboardButton(text="⚙️ Установить", callback_data="setup_guide")
            ],
            
            # Одна кнопка во втором ряду
            [InlineKeyboardButton(text="🔄 Передать подписку", callback_data="transfer_subscription")],
            
            # Кнопка назад
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_user_menu")]
        ]
    )

def get_apps_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора приложений"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            # Две кнопки в первом ряду
            [
                InlineKeyboardButton(text="iOS", callback_data="app_ios"),
                InlineKeyboardButton(text="Android", callback_data="app_android")
            ],
            
            # Две кнопки во втором ряду
            [
                InlineKeyboardButton(text="Windows", callback_data="app_windows"),
                InlineKeyboardButton(text="macOS", callback_data="app_macos")
            ],
            
            # Кнопка назад
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="my_subscription")]
        ]
    )

def get_transfer_confirmation_keyboard(target_user_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения передачи подписки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_transfer_{target_user_id}"),
                InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_transfer")
            ]
        ]
    )

def get_back_button(back_to: str = "back_to_user_menu") -> InlineKeyboardMarkup:
    """Универсальная кнопка 'Назад'"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data=back_to)]
        ]
    )

def get_support_options() -> InlineKeyboardMarkup:
    """Клавиатура вариантов поддержки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Чат с поддержкой", url="https://t.me/your_support_bot")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_to_user_menu")]
        ]
    )

def get_setup_guide_options() -> InlineKeyboardMarkup:
    """Клавиатура инструкций по настройке"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📄 Текстовая инструкция", callback_data="text_guide")],
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="my_subscription")]
        ]
    )
