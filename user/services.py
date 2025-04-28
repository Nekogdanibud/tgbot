import aiohttp
from datetime import datetime
from config import Config
from utils import get_marzban_token, format_traffic
from .texts import UserTexts

class UserService:
    @staticmethod
    def _format_expiry_date(expire_timestamp: int) -> str:
        """Внутренний метод для форматирования даты"""
        if not expire_timestamp:
            return "Бессрочно"
        return datetime.fromtimestamp(expire_timestamp).strftime("%d.%m.%Y %H:%M")

    @staticmethod
    async def get_user_subscription(telegram_id: int):
        """Получает данные подписки пользователя"""
        marzban_username = await get_marzban_username(telegram_id)
        if not marzban_username:
            return None

        try:
            token = await get_marzban_token()
            headers = {"Authorization": f"Bearer {token}"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{Config.MARZBAN_URL}/api/user/{marzban_username}",
                    headers=headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
                    
                    return {
                        "username": marzban_username,
                        "used": format_traffic(data.get("used_traffic", 0)),
                        "total": format_traffic(data.get("data_limit", 0)),
                        "expire": UserService._format_expiry_date(data.get("expire"))
                    }
        except Exception as e:
            raise Exception(f"Ошибка получения данных: {str(e)}")
