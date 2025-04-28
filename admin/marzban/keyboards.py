from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from .texts import *

def marzban_main_kb():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text=SERVER_STATS_BTN, callback_data="marzban:stats"),
        InlineKeyboardButton(text=PROXY_USERS_BTN, callback_data="marzban:users"),
    )
    builder.row(
        InlineKeyboardButton(text=BACK_TO_MAIN_BTN, callback_data="nav:main")
    )
    return builder.as_markup()

def users_list_kb(users: list, page: int = 0, per_page: int = 9):
    builder = InlineKeyboardBuilder()
    
    if not users:
        builder.button(text="❌ Нет пользователей", callback_data="none")
        return builder.as_markup()
    
    # Текущая страница
    start_idx = page * per_page
    end_idx = start_idx + per_page
    page_users = users[start_idx:end_idx]
    
    # Добавляем кнопки по 3 в ряд
    for i in range(0, len(page_users), 3):
        row = page_users[i:i+3]
        buttons = [
            InlineKeyboardButton(
                text=USER_BUTTON_TEMPLATE.format(
                    USER_STATUS_ICONS.get(user.get('status', 'active'), '⚪'),
                    user.get('username', 'N/A')
                ),
                callback_data=f"marzban:user:{user['username']}"
            )
            for user in row
        ]
        builder.row(*buttons)
    
    # Пагинация
    if len(users) > per_page:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(
                InlineKeyboardButton(text="◀️ Назад", callback_data=f"marzban:users:{page-1}")
            )
        if end_idx < len(users):
            nav_buttons.append(
                InlineKeyboardButton(text="Вперед ▶️", callback_data=f"marzban:users:{page+1}")
            )
        if nav_buttons:
            builder.row(*nav_buttons)
    
    builder.row(
        InlineKeyboardButton(text="🔙 Назад", callback_data="admin:marzban")
    )
    return builder.as_markup()

def user_actions_kb(username: str):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="🔄 Обновить", callback_data=f"marzban:refresh:{username}"),
        InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"marzban:edit:{username}"),
        InlineKeyboardButton(text="🗑 Удалить", callback_data=f"marzban:delete:{username}"),
    )
    builder.row(
        InlineKeyboardButton(text="🔙 К списку", callback_data="marzban:users:0")
    )
    return builder.as_markup()
