import logging
import sqlite3
import random
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from database import get_unpaired_students, add_unpaired_student, clear_unpaired_students

# Настройка логирования
logger = logging.getLogger(__name__)

def schedule_jobs(scheduler: AsyncIOScheduler, bot):
    """Настройка планировщика для Random Coffee и Mock Interview."""
    # Планируем Random Coffee каждую пятницу в 10:00
    scheduler.add_job(
        organize_random_coffee,
        trigger='cron',
        day_of_week='fri',
        hour=10,
        minute=0,
        args=[bot],
        id='random_coffee_job'
    )
    logger.info("Запланирована задача Random Coffee: каждую пятницу в 10:00")

    # Планируем Mock Interview каждую среду в 10:00
    scheduler.add_job(
        organize_mock_interview,
        trigger='cron',
        day_of_week='wed',
        hour=10,
        minute=0,
        args=[bot],
        id='mock_interview_job'
    )
    logger.info("Запланирована задача Mock Interview: каждую среду в 10:00")

async def organize_random_coffee(bot):
    """Организация Random Coffee: формирование и уведомление пар."""
    logger.info("Запуск формирования пар для Random Coffee")
    
    students = get_unpaired_students("random_coffee")
    if len(students) < 2:
        logger.warning("Недостаточно студентов для Random Coffee")
        return
    
    random.shuffle(students)
    clear_unpaired_students("random_coffee")
    
    for i in range(0, len(students) - 1, 2):
        student1 = students[i]
        student2 = students[i + 1]
        
        try:
            await bot.send_message(
                chat_id=student1,
                text=f"Ваша пара для Random Coffee: @{student2}. Свяжитесь и договоритесь о встрече!"
            )
            await bot.send_message(
                chat_id=student2,
                text=f"Ваша пара для Random Coffee: @{student1}. Свяжитесь и договоритесь о встрече!"
            )
            logger.info(f"Сформирована пара для Random Coffee: {student1} и {student2}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления для Random Coffee ({student1}, {student2}): {e}")
            add_unpaired_student(student1, "random_coffee")
            add_unpaired_student(student2, "random_coffee")
    
    if len(students) % 2 == 1:
        unpaired = students[-1]
        add_unpaired_student(unpaired, "random_coffee")
        logger.info(f"Студент {unpaired} остался без пары и добавлен в unpaired")

async def organize_mock_interview(bot):
    """Организация Mock Interview: формирование и уведомление пар."""
    logger.info("Запуск формирования пар для Mock Interview")
    
    students = get_unpaired_students("mock_interview")
    if len(students) < 2:
        logger.warning("Недостаточно студентов для Mock Interview")
        return
    
    random.shuffle(students)
    clear_unpaired_students("mock_interview")
    
    for i in range(0, len(students) - 1, 2):
        student1 = students[i]
        student2 = students[i + 1]
        
        try:
            await bot.send_message(
                chat_id=student1,
                text=f"Ваша пара для Mock Interview: @{student2}. Свяжитесь и договоритесь о собеседовании!"
            )
            await bot.send_message(
                chat_id=student2,
                text=f"Ваша пара для Mock Interview: @{student1}. Свяжитесь и договоритесь о собеседовании!"
            )
            logger.info(f"Сформирована пара для Mock Interview: {student1} и {student2}")
        except Exception as e:
            logger.error(f"Ошибка отправки уведомления для Mock Interview ({student1}, {student2}): {e}")
            add_unpaired_student(student1, "mock_interview")
            add_unpaired_student(student2, "mock_interview")
    
    if len(students) % 2 == 1:
        unpaired = students[-1]
        add_unpaired_student(unpaired, "mock_interview")
        logger.info(f"Студент {unpaired} остался без пары и добавлен в unpaired")