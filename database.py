import aiosqlite
import asyncio
import logging
import atexit
from typing import Optional, List, Tuple, Dict, Any, AsyncGenerator
from contextlib import asynccontextmanager
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    _instance = None
    
    def __new__(cls, db_path: str = 'marzban_bot.db'):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db_path = db_path
            cls._instance.conn = None
            cls._instance._cleanup_registered = False
            cls._instance._lock = asyncio.Lock()
        return cls._instance
    
    async def connect(self) -> None:
        """Устанавливаем и инициализируем соединение с базой данных"""
        async with self._lock:
            if self.conn is None:
                try:
                    self.conn = await aiosqlite.connect(self.db_path)
                    await self.conn.execute("PRAGMA journal_mode=WAL")
                    await self.conn.execute("PRAGMA foreign_keys=ON")
                    await self._ensure_tables()
                    
                    if not self._cleanup_registered:
                        atexit.register(self.sync_cleanup)
                        self._cleanup_registered = True
                        
                    logger.info(f"Database connected to {self.db_path}")
                except Exception as e:
                    logger.error(f"Database connection failed: {e}")
                    raise
    
    def sync_cleanup(self) -> None:
        """Синхронный метод для корректного завершения работы"""
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self._cleanup())
            else:
                loop.run_until_complete(self._cleanup())
        except Exception as e:
            logger.error(f"Cleanup error: {e}")

    async def _cleanup(self) -> None:
        """Асинхронное закрытие соединения с БД"""
        async with self._lock:
            if self.conn is not None:
                try:
                    await self.conn.close()
                    logger.info("Database connection closed gracefully")
                except Exception as e:
                    logger.error(f"Error closing connection: {e}")
                finally:
                    self.conn = None

    async def _ensure_tables(self) -> None:
        """Создаем необходимые таблицы при инициализации"""
        try:
            # Таблица пользователей
            await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                marzban_username TEXT PRIMARY KEY,
                telegram_id INTEGER UNIQUE,
                is_admin BOOLEAN DEFAULT FALSE,
                is_moderator BOOLEAN DEFAULT FALSE,
                is_banned BOOLEAN DEFAULT FALSE,
                ban_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # Таблица заявок для админки
            await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS admin_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                request_text TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                processed_at TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES users(telegram_id)
            )''')

            # Индексы для ускорения запросов
            await self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_users_telegram_id ON users(telegram_id)
            ''')
            
            await self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_admin_requests_user_id ON admin_requests(user_id)
            ''')

            await self.conn.commit()
            logger.info("Database tables initialized")
        except Exception as e:
            logger.error(f"Table creation failed: {e}")
            raise

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[None, None]:
        """Контекстный менеджер для транзакций"""
        await self.connect()
        try:
            await self.conn.execute("BEGIN")
            yield
            await self.conn.commit()
        except Exception as e:
            await self.conn.rollback()
            logger.error(f"Transaction failed: {e}")
            raise

    async def execute(self, query: str, params: tuple = (), retry: bool = True) -> aiosqlite.Cursor:
        """Безопасное выполнение SQL-запроса"""
        try:
            await self.connect()
            return await self.conn.execute(query, params)
        except Exception as e:
            if retry:
                logger.warning(f"Retrying query: {query[:100]}...")
                await asyncio.sleep(0.1)
                return await self.execute(query, params, retry=False)
            logger.error(f"Query failed: {query[:100]}... Error: {e}")
            raise

    # Основные методы API
    async def get_telegram_id(self, marzban_username: str) -> Optional[int]:
        """Получить Telegram ID по имени пользователя Marzban"""
        cursor = await self.execute(
            'SELECT telegram_id FROM users WHERE marzban_username = ?',
            (marzban_username,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None

    async def get_marzban_username(self, telegram_id: int) -> Optional[str]:
        """Получить имя пользователя Marzban по Telegram ID"""
        cursor = await self.execute(
            'SELECT marzban_username FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        result = await cursor.fetchone()
        return result[0] if result else None

    async def update_telegram_id(self, marzban_username: str, telegram_id: int) -> None:
        """Обновить или добавить связку Marzban-Telegram"""
        async with self.transaction():
            await self.execute(
                '''
                INSERT OR REPLACE INTO users (marzban_username, telegram_id)
                VALUES (?, ?)
                ''',
                (marzban_username, telegram_id)
            )

    # Методы для админ-панели
    async def is_admin(self, user_id: int) -> bool:
        """Проверить, является ли пользователь администратором"""
        cursor = await self.execute(
            'SELECT is_admin FROM users WHERE telegram_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return bool(result and result[0])

    async def is_moderator(self, user_id: int) -> bool:
        """Проверить, является ли пользователь модератором"""
        cursor = await self.execute(
            'SELECT is_moderator FROM users WHERE telegram_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return bool(result and result[0])

    async def is_banned(self, user_id: int) -> bool:
        """Проверить, забанен ли пользователь"""
        cursor = await self.execute(
            'SELECT is_banned FROM users WHERE telegram_id = ?',
            (user_id,)
        )
        result = await cursor.fetchone()
        return bool(result and result[0])

    async def set_admin(self, user_id: int, is_admin: bool = True) -> None:
        """Назначить/снять администратора"""
        async with self.transaction():
            await self.execute(
                'UPDATE users SET is_admin = ? WHERE telegram_id = ?',
                (is_admin, user_id)
            )

    async def set_moderator(self, user_id: int, is_moderator: bool = True) -> None:
        """Назначить/снять модератора"""
        async with self.transaction():
            await self.execute(
                'UPDATE users SET is_moderator = ? WHERE telegram_id = ?',
                (is_moderator, user_id)
            )

    async def ban_user(self, user_id: int, reason: str = None) -> None:
        """Забанить пользователя"""
        async with self.transaction():
            await self.execute(
                'UPDATE users SET is_banned = TRUE, ban_reason = ? WHERE telegram_id = ?',
                (reason, user_id)
            )

    async def unban_user(self, user_id: int) -> None:
        """Разбанить пользователя"""
        async with self.transaction():
            await self.execute(
                'UPDATE users SET is_banned = FALSE, ban_reason = NULL WHERE telegram_id = ?',
                (user_id,)
            )

    async def get_all_users(self) -> List[Tuple[str, int]]:
        """Получить список всех пользователей"""
        cursor = await self.execute(
            'SELECT marzban_username, telegram_id FROM users'
        )
        return await cursor.fetchall()

    async def get_active_users(self) -> List[Dict[str, Any]]:
        """Получить список активных пользователей"""
        cursor = await self.execute(
            '''
            SELECT telegram_id, marzban_username
            FROM users
            WHERE is_banned = FALSE
            '''
        )
        return [{'telegram_id': row[0], 'username': row[1]} for row in await cursor.fetchall()]

    async def get_active_users_count(self) -> int:
        """Получить количество активных пользователей"""
        cursor = await self.execute(
            'SELECT COUNT(*) FROM users WHERE is_banned = FALSE'
        )
        return (await cursor.fetchone())[0]

    async def is_tgid_exists(self, telegram_id: int) -> bool:
        """Проверить существование Telegram ID"""
        cursor = await self.execute(
            'SELECT 1 FROM users WHERE telegram_id = ?',
            (telegram_id,)
        )
        return await cursor.fetchone() is not None

    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе"""
        cursor = await self.execute(
            '''
            SELECT 
                telegram_id,
                marzban_username as username,
                CASE 
                    WHEN is_admin THEN 'admin'
                    WHEN is_moderator THEN 'moder'
                    ELSE 'user'
                END as status,
                is_banned,
                ban_reason,
                created_at as reg_date
            FROM users
            WHERE telegram_id = ?
            ''',
            (user_id,)
        )
        result = await cursor.fetchone()
        if not result:
            return None
        
        return {
            'telegram_id': result[0],
            'username': result[1],
            'status': result[2],
            'is_banned': bool(result[3]),
            'ban_reason': result[4],
            'reg_date': result[5]
        }

    # Методы для работы с заявками
    async def get_requests(self, status: str = None) -> List[Dict[str, Any]]:
        """Получить список заявок"""
        if status:
            cursor = await self.execute(
                '''
                SELECT ar.id, ar.user_id, ar.request_text, ar.status, ar.processed_at,
                       u.marzban_username as username
                FROM admin_requests ar
                LEFT JOIN users u ON ar.user_id = u.telegram_id
                WHERE ar.status = ?
                ORDER BY ar.id DESC
                ''',
                (status,)
            )
        else:
            cursor = await self.execute(
                '''
                SELECT ar.id, ar.user_id, ar.request_text, ar.status, ar.processed_at,
                       u.marzban_username as username
                FROM admin_requests ar
                LEFT JOIN users u ON ar.user_id = u.telegram_id
                ORDER BY ar.id DESC
                '''
            )
        
        return [
            {
                'id': row[0],
                'user_id': row[1],
                'text': row[2],
                'status': row[3],
                'processed_at': row[4],
                'username': row[5]
            }
            for row in await cursor.fetchall()
        ]

    async def get_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """Получить детали конкретной заявки"""
        cursor = await self.execute(
            '''
            SELECT ar.id, ar.user_id, ar.request_text, ar.status, ar.processed_at,
                   u.marzban_username as username
            FROM admin_requests ar
            LEFT JOIN users u ON ar.user_id = u.telegram_id
            WHERE ar.id = ?
            ''',
            (request_id,)
        )
        result = await cursor.fetchone()
        if not result:
            return None
        
        return {
            'id': result[0],
            'user_id': result[1],
            'text': result[2],
            'status': result[3],
            'processed_at': result[4],
            'username': result[5]
        }

    async def create_request(self, user_id: int, request_text: str) -> int:
        """Создать новую заявку"""
        async with self.transaction():
            cursor = await self.execute(
                '''
                INSERT INTO admin_requests (user_id, request_text)
                VALUES (?, ?)
                ''',
                (user_id, request_text)
            )
            return cursor.lastrowid

    async def approve_request(self, request_id: int) -> None:
        """Одобрить заявку"""
        async with self.transaction():
            await self.execute(
                '''
                UPDATE admin_requests 
                SET status = 'approved', processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (request_id,)
            )

    async def reject_request(self, request_id: int) -> None:
        """Отклонить заявку"""
        async with self.transaction():
            await self.execute(
                '''
                UPDATE admin_requests 
                SET status = 'rejected', processed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                ''',
                (request_id,)
            )

    async def get_stats(self) -> Dict[str, Any]:
        """Получить статистику бота"""
        async with self.transaction():
            cursor = await self.execute('SELECT COUNT(*) FROM users')
            total_users = (await cursor.fetchone())[0]
            
            cursor = await self.execute(
                'SELECT COUNT(*) FROM users WHERE is_admin = 1 OR is_moderator = 1'
            )
            active_staff = (await cursor.fetchone())[0]
            
            cursor = await self.execute(
                'SELECT COUNT(*) FROM admin_requests WHERE status = "pending"'
            )
            pending_requests = (await cursor.fetchone())[0]
            
            cursor = await self.execute(
                'SELECT COUNT(*) FROM users WHERE is_banned = 1'
            )
            banned_users = (await cursor.fetchone())[0]
            
            return {
                'total_users': total_users,
                'active_staff': active_staff,
                'pending_requests': pending_requests,
                'banned_users': banned_users
            }

# Функции для обратной совместимости
async def init_db() -> None:
    """Инициализировать базу данных (для обратной совместимости)"""
    db = Database()
    await db.connect()

async def get_telegram_id(marzban_username: str) -> Optional[int]:
    """Получить Telegram ID (для обратной совместимости)"""
    db = Database()
    return await db.get_telegram_id(marzban_username)

async def get_marzban_username(telegram_id: int) -> Optional[str]:
    """Получить Marzban username (для обратной совместимости)"""
    db = Database()
    return await db.get_marzban_username(telegram_id)

async def update_telegram_id(marzban_username: str, telegram_id: int) -> None:
    """Обновить связку (для обратной совместимости)"""
    db = Database()
    await db.update_telegram_id(marzban_username, telegram_id)

async def get_all_users() -> List[Tuple[str, int]]:
    """Получить всех пользователей (для обратной совместимости)"""
    db = Database()
    return await db.get_all_users()

async def is_tgid_exists(telegram_id: int) -> bool:
    """Проверить существование ID (для обратной совместимости)"""
    db = Database()
    return await db.is_tgid_exists(telegram_id)

async def is_admin(user_id: int) -> bool:
    """Проверить админа (для обратной совместимости)"""
    db = Database()
    return await db.is_admin(user_id)
