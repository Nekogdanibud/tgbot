class AdminTexts:
    # Основные сообщения
    WELCOME = "👮‍♂️ Добро пожаловать в админ-панель"
    ACCESS_DENIED = "⛔ У вас нет прав доступа!"
    
    # Меню
    MAIN_MENU = "📌 Выберите раздел:"
    STATS = (
        "📊 Статистика бота:\n"
        "┌ Пользователей: {users_count}\n"
        "├ Активных: {active_users}\n"
        "└ Заявок: {requests_count}"
    )
    
    # Работа с заявками
    REQUESTS_LIST = "📋 Список заявок:"
    REQUEST_DETAIL = (
        "📄 Заявка #{id}\n"
        "┌ Пользователь: {username}\n"
        "├ Дата: {date}\n"
        "└ Текст: {text}\n"
        "Выберите действие:"
    )
    REQUEST_APPROVED = "✅ Заявка #{id} одобрена"
    REQUEST_REJECTED = "❌ Заявка #{id} отклонена"
    
    # Управление пользователями
    USERS_LIST = "👥 Список пользователей:"
    USER_DETAIL = (
        "👤 Пользователь #{id}\n"
        "┌ Ник: @{username}\n"
        "├ Статус: {status}\n"
        "└ Регистрация: {reg_date}\n"
        "Выберите действие:"
    )
    USER_BANNED = "🚫 Пользователь @{username} заблокирован"
    USER_UNBANNED = "🟢 Пользователь @{username} разблокирован"
    
    # Рассылка
    BROADCAST_START = "📢 Введите текст рассылки:"
    BROADCAST_CONFIRM = (
        "Подтвердите рассылку:\n"
        "➖➖➖\n"
        "{text}\n"
        "➖➖➖\n"
        "Получателей: {count}"
    )
    BROADCAST_SUCCESS = "✅ Рассылка завершена (доставлено: {success}/{total})"
    BROADCAST_CANCELLED = "❌ Рассылка отменена"
    MODER_WELCOME = (
        "🛠 Вы вошли как модератор\n"
        "Доступные вам функции:"
    )

class AdminButtons:
    # Основные кнопки
    BACK = "🔙 Назад"
    CANCEL = "❌ Отмена"
    CONFIRM = "✅ Подтвердить"
    
    # Меню
    REQUESTS = "📨 Заявки"
    USERS = "👥 Пользователи"
    STATS = "📊 Статистика"
    BROADCAST = "📢 Рассылка"
    MARZBAN = "👻 Управление Marzban"
    
    # Действия
    APPROVE = "✅ Одобрить"
    REJECT = "❌ Отклонить"
    BAN = "🚫 Забанить"
    UNBAN = "🟢 Разбанить"
    NEXT = "⏭ Далее"
    PREV = "⏮ Назад"

