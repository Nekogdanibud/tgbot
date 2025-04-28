import requests
from requests.auth import HTTPBasicAuth
from typing import Optional, Dict, Any, List
import sys
from pathlib import Path
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Добавляем родительскую директорию в путь
sys.path.append(str(Path(__file__).parent.parent))
from config import Config

class MarzbanAPI:
    def __init__(self):
        """Инициализация API клиента"""
        self.base_url = Config.MARZBAN_URL.rstrip('/')
        self.username = Config.MARZBAN_USERNAME
        self.password = Config.MARZBAN_PASSWORD
        self.token = None
        self._get_token()
        logger.info(f"MarzbanAPI initialized for {self.base_url}")

    def _get_token(self) -> None:
        """Получение и обновление токена авторизации"""
        endpoint = f"{self.base_url}/api/admin/token"
        auth = HTTPBasicAuth(self.username, self.password)
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password
        }
        
        try:
            logger.debug(f"Requesting token from {endpoint}")
            response = requests.post(endpoint, data=data, auth=auth)
            response.raise_for_status()
            
            self.token = response.json().get("access_token")
            if not self.token:
                raise ValueError("Empty access token received")
            
            logger.info("Successfully obtained access token")
        except requests.exceptions.RequestException as e:
            logger.error(f"Token request failed: {str(e)}")
            raise ConnectionError(f"Could not connect to Marzban API: {str(e)}")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Базовый метод для выполнения запросов с обработкой ошибок"""
        if not self.token:
            self._get_token()
            
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        
        url = f"{self.base_url}{endpoint}"
        logger.debug(f"Making {method} request to {url}")
        
        try:
            response = requests.request(
                method, 
                url, 
                headers=headers, 
                timeout=30,
                **kwargs
            )
            
            logger.debug(f"Response status: {response.status_code}")
            logger.debug(f"Response content: {response.text[:200]}...")
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {str(e)}")
            raise ConnectionError(f"API request failed: {str(e)}")

    def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Создание нового пользователя с обязательными параметрами"""
        endpoint = "/api/user"
        
        # Обязательные параметры по умолчанию
        default_data = {
            "proxies": {
                "vmess": {"id": ""},  # Пустой ID сгенерируется автоматически
                "vless": {"id": ""},
                "trojan": {"password": ""},
                "shadowsocks": {"password": ""}
            },
            "inbounds": {
                "vmess": ["VMESS_INBOUND"],
                "vless": ["VLESS TCP REALITY"],
                "trojan": ["TROJAN_INBOUND"],
                "shadowsocks": ["SHADOWSOCKS_INBOUND"]
            },
            "data_limit": 1073741824,  # 1GB
            "data_limit_reset_strategy": "no_reset",
            "expire": None,  # Бессрочный
            "status": "active",
            "note": ""
        }
        
        # Объединяем с пользовательскими данными
        payload = {**default_data, **user_data}
        
        # Валидация
        if "username" not in payload:
            raise ValueError("Username is required")
        
        return self._make_request("POST", endpoint, json=payload)

    def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Получение информации о пользователе"""
        endpoint = f"/api/user/{username}"
        try:
            return self._make_request("GET", endpoint)
        except Exception as e:
            if "404" in str(e):
                logger.warning(f"User {username} not found")
                return None
            raise

    def update_user(self, username: str, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновление данных пользователя"""
        endpoint = f"/api/user/{username}"
        return self._make_request("PUT", endpoint, json=user_data)

    def delete_user(self, username: str) -> bool:
        """Удаление пользователя"""
        endpoint = f"/api/user/{username}"
        try:
            self._make_request("DELETE", endpoint)
            logger.info(f"User {username} deleted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {username}: {str(e)}")
            return False

    def get_users(self, status: Optional[str] = None, offset: int = 0, limit: int = 100) -> List[Dict[str, Any]]:
        """Получение списка пользователей с пагинацией"""
        endpoint = "/api/users"
        params = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        
        response = self._make_request("GET", endpoint, params=params)
        return response.get("users", [])

    def get_system_stats(self) -> Dict[str, Any]:
        """Получение статистики системы"""
        endpoint = "/api/system"
        return self._make_request("GET", endpoint)

    def revoke_user_subscription(self, username: str) -> Dict[str, Any]:
        """Отзыв подписки пользователя"""
        endpoint = f"/api/user/{username}/revoke_sub"
        return self._make_request("POST", endpoint)

    def reset_user_traffic(self, username: str) -> Dict[str, Any]:
        """Сброс трафика пользователя"""
        endpoint = f"/api/user/{username}/reset_traffic"
        return self._make_request("POST", endpoint)

    def get_user_usage(self, username: str) -> Dict[str, Any]:
        """Получение статистики использования пользователя"""
        endpoint = f"/api/user/{username}/usage"
        return self._make_request("GET", endpoint)

    def get_all_nodes(self) -> List[Dict[str, Any]]:
        """Получение списка всех узлов"""
        endpoint = "/api/nodes"
        return self._make_request("GET", endpoint).get("nodes", [])

    def get_node(self, node_id: int) -> Dict[str, Any]:
        """Получение информации об узле"""
        endpoint = f"/api/node/{node_id}"
        return self._make_request("GET", endpoint)
