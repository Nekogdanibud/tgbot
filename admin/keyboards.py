from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from admin.texts import AdminButtons

def admin_main_kb():
    """Главное меню админа (инлайн)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=AdminButtons.REQUESTS, callback_data="nav:requests"),
                InlineKeyboardButton(text=AdminButtons.USERS, callback_data="nav:users")
            ],
            [
                InlineKeyboardButton(text=AdminButtons.STATS, callback_data="nav:stats"),
                InlineKeyboardButton(text=AdminButtons.BROADCAST, callback_data="nav:broadcast")
            ],
            [
                InlineKeyboardButton(text=AdminButtons.MARZBAN, callback_data="admin:marzban")  # Новая кнопка
            ]
        ]
    )

def moder_kb():
    """Главное меню модератора (инлайн)"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=AdminButtons.REQUESTS, callback_data="nav:requests"),
                InlineKeyboardButton(text=AdminButtons.STATS, callback_data="nav:stats")
            ],
            [
                InlineKeyboardButton(text=AdminButtons.BACK, callback_data="nav:main")
            ]
        ]
    )

def cancel_kb():
    """Кнопка отмены действия"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=AdminButtons.CANCEL, callback_data="nav:cancel")]
        ]
    )

def confirm_broadcast_kb():
    """Подтверждение рассылки"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=AdminButtons.CONFIRM, callback_data="action:broadcast:confirm"),
                InlineKeyboardButton(text=AdminButtons.CANCEL, callback_data="nav:cancel")
            ]
        ]
    )

def requests_list_kb(requests, offset=0, limit=10):
    """Список заявок с пагинацией"""
    buttons = []
    
    # Кнопки заявок
    for request in requests[offset:offset+limit]:
        buttons.append(
            [InlineKeyboardButton(
                text=f"#{request['id']} @{request['username']}",
                callback_data=f"nav:requests:detail:{request['id']}"
            )]
        )
    
    # Пагинация
    pagination = []
    if offset > 0:
        pagination.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"nav:requests:page:{max(0, offset-limit)}"
            )
        )
    if offset + limit < len(requests):
        pagination.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"nav:requests:page:{offset+limit}"
            )
        )
    if pagination:
        buttons.append(pagination)
    
    # Кнопка возврата
    buttons.append(
        [InlineKeyboardButton(text=AdminButtons.BACK, callback_data="nav:main")]
    )
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def request_actions_kb(request_id):
    """Действия с заявкой"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=AdminButtons.APPROVE,
                    callback_data=f"action:requests:approve:{request_id}"
                ),
                InlineKeyboardButton(
                    text=AdminButtons.REJECT,
                    callback_data=f"action:requests:reject:{request_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=AdminButtons.BACK,
                    callback_data="nav:requests"
                )
            ]
        ]
    )

def users_list_kb(users, offset=0, limit=10):
    """Список пользователей с пагинацией"""
    buttons = []
    
    # Кнопки пользователей
    for user in users[offset:offset+limit]:
        status_icon = "🟢" if not user.get('is_banned', False) else "🔴"
        buttons.append(
            [InlineKeyboardButton(
                text=f"{status_icon} @{user['username']} ({user['status']})",
                callback_data=f"nav:users:detail:{user['id']}"
            )]
        )
    
    # Пагинация
    pagination = []
    if offset > 0:
        pagination.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"nav:users:page:{max(0, offset-limit)}"
            )
        )
    if offset + limit < len(users):
        pagination.append(
            InlineKeyboardButton(
                text="Вперёд ➡️",
                callback_data=f"nav:users:page:{offset+limit}"
            )
        )
    if pagination:
        buttons.append(pagination)
    
    # Кнопка возврата
    buttons.append(
        [InlineKeyboardButton(text=AdminButtons.BACK, callback_data="nav:main")]
    )
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def user_actions_kb(user_id, is_banned):
    """Действия с пользователем"""
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=AdminButtons.UNBAN if is_banned else AdminButtons.BAN,
                    callback_data=f"action:users:unban:{user_id}" if is_banned else f"action:users:ban:{user_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    text=AdminButtons.BACK,
                    callback_data="nav:users"
                )
            ]
        ]
    )
