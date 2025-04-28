import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from config import Config
from database import Database
from admin.admin_router import admin_router
from admin.marzban.handlers import router as marzban_router
from user.user_router import user_router
from user.keyboards import get_user_main_menu
from admin.admin_actions import AdminActions
from admin.keyboards import admin_main_kb

async def on_startup():
    """Инициализация при запуске"""
    db = Database()
    await db.connect()
    logging.info("Database initialized")

async def start_handler(message: Message):
    db = Database()
    actions = AdminActions()
    
    if await db.is_admin(message.from_user.id):
        await message.answer(
            text="👮‍♂️ Добро пожаловать в админ-панель",
            reply_markup=admin_main_kb()
        )
    elif await db.is_moderator(message.from_user.id):
        await message.answer(
            text="🛠 Вы вошли как модератор",
            reply_markup=moder_kb()
        )
    else:
        await message.answer(
            "👋 Добро пожаловать!",
            reply_markup=get_user_main_menu()
        )

async def main():
    bot = Bot(token=Config.BOT_TOKEN)
    dp = Dispatcher()

    dp.message.register(start_handler, Command("start"))
    dp.include_router(admin_router)
    dp.include_router(user_router)
    dp.include_router(marzban_router)
    await on_startup()
    logging.info("Bot started")
    
    try:
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
    except Exception as e:
        logging.error(f"Fatal error: {e}", exc_info=True)
    finally:
        db = Database()
        await db._cleanup()

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    asyncio.run(main())
