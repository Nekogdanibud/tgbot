class UserTexts:
    START = "👋 Добро пожаловать в VPN сервис!\nВыберите действие:"
    
    @staticmethod
    def subscription_info(username: str, used: str, total: str, expire: str) -> str:
        return (
            f"📋 Ваша подписка:\n"
            f"├ Имя пользователя: {username}\n"
            f"├ Использовано трафика: {used}\n"
            f"├ Всего трафика: {total}\n"
            f"└ Срок действия: {expire}"
        )
    
    NO_SUBSCRIPTION = "У вас нет активной подписки."
    SUBSCRIPTION_ERROR = "Ошибка при получении данных. Попробуйте позже."
    APPS_MENU = "Выберите приложение для скачивания:"
    
    SETUP_GUIDE = (
        "📖 Инструкция по настройке VPN:\n"
        "1. Скачайте приложение из раздела 'Скачать приложение'.\n"
        "2. Используйте ваши учетные данные для входа.\n"
        "3. Следуйте инструкциям в приложении.\n"
        "Если возникнут вопросы, обратитесь в поддержку."
    )
    
    TRANSFER_REQUEST = "Введите Telegram ID пользователя, которому хотите передать подписку:"
    INVALID_TRANSFER_ID = "Пожалуйста, введите корректный Telegram ID (только цифры)."
    NO_SUBSCRIPTION_TO_TRANSFER = "У вас нет подписки для переноса."
    TRANSFER_SUCCESS = "Подписка для {username} успешно передана пользователю с ID {new_id}."
    TRANSFER_ERROR = "Ошибка при переносе подписки. Попробуйте позже."
    
    HOW_TO_USE = (
        "ℹ️ Как использовать VPN сервис:\n"
        "1. Проверьте статус подписки в разделе 'Моя подписка'.\n"
        "2. Скачайте приложение в разделе 'Скачать приложение'.\n"
        "3. Следуйте инструкциям в разделе 'Инструкция по настройке'.\n"
        "4. Для помощи обратитесь в 'Поддержка'."
    )
    
    @staticmethod
    def support(username: str) -> str:
        return f"📞 Поддержка:\nСвяжитесь с нами через @{username}"
    
    MAIN_MENU = "Главное меню:"
