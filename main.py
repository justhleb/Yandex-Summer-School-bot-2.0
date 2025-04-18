import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.registration import register_handlers as register_registration
from handlers.admin import register_handlers as register_admin
from handlers.scheduler import schedule_jobs
from database import init_db

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция для запуска бота."""
    # Инициализация базы данных
    init_db()
    
    # Инициализация бота и диспетчера
    bot = Bot(token="7380357980:AAFzhfgLQN25MSS9nWbJNgCRLmf6BAto0p4")
    dp = Dispatcher(storage=MemoryStorage())
    
    # Регистрация обработчиков (админка регистрируется первой для приоритета)
    register_admin(dp)
    register_registration(dp)
    
    # Инициализация планировщика
    scheduler = AsyncIOScheduler()
    schedule_jobs(scheduler, bot)
    scheduler.start()
    
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    asyncio.run(main())