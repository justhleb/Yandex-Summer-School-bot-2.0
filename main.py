import logging
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from handlers.registration import register_handlers as register_registration
from handlers.admin import register_handlers as register_admin
from handlers.scheduler import organize_random_coffee, organize_mock_interview
from handlers.reminders import send_lecture_reminders
from database import init_db
from datetime import datetime

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
    # Инициализация базы данных
    init_db()

    # Инициализация бота
    bot = Bot(token='7380357980:AAFzhfgLQN25MSS9nWbJNgCRLmf6BAto0p4')
    dp = Dispatcher(storage=MemoryStorage())

    # Удаление существующего webhook
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook успешно удалён")
    except Exception as e:
        logger.error(f"Ошибка при удалении webhook: {e}")

    # Регистрация обработчиков
    register_registration(dp)
    register_admin(dp)

    # Настройка планировщика задач
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        organize_random_coffee,
        'cron',
        day_of_week='mon',
        hour=9,
        minute=0,
        args=[bot],
        timezone='Europe/Moscow'
    )
    scheduler.add_job(
        organize_mock_interview,
        'cron',
        day_of_week='wed',
        hour=9,
        minute=0,
        args=[bot],
        timezone='Europe/Moscow'
    )
    scheduler.add_job(
        send_lecture_reminders,
        'cron',
        hour=12,
        minute=0,
        args=[bot],
        timezone='Europe/Moscow'
    )
    scheduler.add_job(
        send_lecture_reminders,
        'cron',
        hour=18,
        minute=0,
        args=[bot],
        timezone='Europe/Moscow'
    )
    scheduler.start()
    logger.info("Планировщик задач запущен")

    # Запуск бота
    try:
        logger.info("Бот запущен")
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())