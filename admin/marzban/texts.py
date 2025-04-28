# Основное меню
MARZBAN_MENU_TITLE = "🔧 Управление Marzban Proxy"
SERVER_STATS_BTN = "📊 Статистика сервера"
PROXY_USERS_BTN = "👥 Пользователи прокси"
BACK_TO_MAIN_BTN = "⬅️ На главную"

# Пользователи
USER_LIST_TITLE = "👥 Список пользователей ({}):"
USER_BUTTON_TEMPLATE = "{} {}"  # Иконка + имя
USER_STATUS_ICONS = {
    "active": "🟢",
    "expired": "🔴",
    "limited": "🟡",
    "disabled": "⚫"
}

# Детали пользователя
USER_DETAILS_TITLE = "🔍 Данные пользователя:\n"
USER_DETAILS = """
<b>Имя:</b> {}
<b>Статус:</b> {}
<b>Лимит:</b> {}
<b>Использовано:</b> {}
<b>Срок:</b> {}
"""

# Статистика
SERVER_STATS_TITLE = "📊 Статистика сервера\n"
STATS_TEMPLATE = """
<b>CPU:</b> {}%
<b>Память:</b> {}%
<b>Пользователей:</b> {}
<b>Активных:</b> {}
"""
