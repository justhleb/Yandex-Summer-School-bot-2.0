import logging
import sqlite3
from aiogram import Bot
from datetime import datetime
from database import get_lectures_for_day

# Настройка логирования
logger = logging.getLogger(__name__)

async def send_lecture_reminders(bot: Bot):
    """Отправка напоминаний о лекциях на текущий день в 12:00 и 18:00."""
    try:
        # Получаем все лекции на текущий день
        lectures = get_lectures_for_day()
        if not lectures:
            logger.info("Лекций на текущий день нет, напоминания не отправлены")
            return

        logger.info(f"Найдено {len(lectures)} лекций для напоминаний")

        # Подключаемся к базе students.db
        conn = sqlite3.connect('students.db')
        c = conn.cursor()

        # Для каждой лекции
        for lecture in lectures:
            lecture_id, school, lecturer, topic, description, link, date, direction = lecture
            logger.info(f"Обработка лекции: {topic}, школа: {school}, направление: {direction}")

            # Получаем студентов, соответствующих школе и направлению лекции
            if direction:
                c.execute("SELECT username FROM students WHERE school = ? AND direction = ?",
                          (school, direction))
            else:
                c.execute("SELECT username FROM students WHERE school = ?",
                          (school,))
            
            students = c.fetchall()
            logger.info(f"Найдено {len(students)} студентов для лекции: {topic}")

            # Формируем сообщение напоминания
            reminder_text = (
                f"Напоминание о лекции!\n"
                f"Тема: {topic}\n"
                f"Лектор: {lecturer}\n"
                f"Дата: {date}\n"
                f"Описание: {description}\n"
                f"Ссылка: {link}"
            )

            # Отправляем напоминание каждому студенту
            for student in students:
                username = student[0]
                try:
                    await bot.send_message(chat_id=username, text=reminder_text)
                    logger.info(f"Напоминание о лекции '{topic}' отправлено студенту {username}")
                except Exception as e:
                    logger.error(f"Ошибка отправки напоминания студенту {username}: {e}")

        conn.close()

    except Exception as e:
        logger.error(f"Ошибка при отправке напоминаний: {e}")