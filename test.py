import sys	
from marzban.api import MarzbanAPI
from config import Config
from pprint import pprint

def print_header(title):
    print(f"\n{'='*50}")
    print(f"{title.upper():^50}")
    print(f"{'='*50}")

def test_connection(api):
    print_header("testing api connection")
    try:
        stats = api.get_system_stats()
        print("✅ Успешное подключение к Marzban API")
        print("Версия Marzban:", stats.get("version"))
        print("Статус:", stats.get("status"))
        return True
    except Exception as e:
        print(f"❌ Ошибка подключения: {str(e)}")
        return False

def test_user_management(api, test_username="test_user_check"):
    print_header("testing user management")
    
    # Создание тестового пользователя
    user_data = {
        "username": test_username,
        "proxies": {
            "vless": {}
        },
        "data_limit": 1073741824,  # 1GB
        "expire": None  # Бессрочный
    }
    
    try:
        # Создание
        print("🔄 Создание тестового пользователя...")
        created_user = api.create_user(user_data)
        print(f"✅ Пользователь создан: {created_user['username']}")
        
        # Получение
        print("\n🔄 Получение информации о пользователе...")
        user_info = api.get_user(test_username)
        pprint(user_info)
        
        # Обновление
        print("\n🔄 Обновление лимита данных (2GB)...")
        updated = api.update_user(test_username, {"data_limit": 2147483648})
        print(f"✅ Новый лимит: {updated['data_limit']/1024/1024/1024:.2f} GB")
        
        # Список пользователей
        print("\n🔄 Получение списка пользователей...")
        users = api.get_users(limit=100)
        print(f"Найдено пользователей: {len(users)}")
       
        for u in users:
            print(f"- {u['username']} (статус: {u['status']})")
        
        return True
    except Exception as e:
        print(f"❌ Ошибка: {str(e)}")
        return False
    finally:
        # Удаление тестового пользователя
        print("\n🔄 Удаление тестового пользователя...")
        if api.delete_user(test_username):
            print("✅ Тестовый пользователь удален")
        else:
            print("❌ Не удалось удалить тестового пользователя")

def main():
    print("🚀 Запуск проверки Marzban API")
    
    try:
        api = MarzbanAPI()
        
        if not test_connection(api):
            sys.exit(1)
            
        if not test_user_management(api):
            sys.exit(1)
            
        print("\n🎉 Все тесты пройдены успешно!")
    except Exception as e:
        print(f"\n🔥 Критическая ошибка: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
