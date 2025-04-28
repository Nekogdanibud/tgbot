# /root/production/utils.py
import requests
from config import Config
from typing import Optional

async def get_marzban_token() -> Optional[str]:
    """Получение токена аутентификации Marzban"""
    try:
        response = requests.post(
            f"{Config.MARZBAN_URL}/api/admin/token",
            data={
                "username": Config.MARZBAN_USERNAME,
                "password": Config.MARZBAN_PASSWORD
            }
        )
        return response.json().get("access_token")
    except Exception as e:
        print(f"Ошибка получения токена: {e}")
        return None

def format_traffic(bytes_size: int) -> str:
    """Форматирование размера трафика"""
    if not bytes_size:
        return "0 B"
    
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if bytes_size < 1024:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.2f} TB"
