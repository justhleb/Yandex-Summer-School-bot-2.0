import logging
import sqlite3
from datetime import datetime, timedelta

# Настройка логирования
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация баз данных students.db и schedule.db."""
    try:
        # Инициализация students.db
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS students
                     (username TEXT PRIMARY KEY, 
                      school TEXT, 
                      direction TEXT, 
                      random_coffee INTEGER, 
                      mock_interview INTEGER)''')
        c.execute('''CREATE TABLE IF NOT EXISTS unpaired_students
                     (username TEXT PRIMARY KEY, 
                      type TEXT, 
                      school TEXT, 
                      direction TEXT)''')
        conn.commit()
        logger.info("Таблицы students и unpaired_students инициализированы")
        
        # Инициализация schedule.db
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS lectures
                     (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                      school TEXT, 
                      lecturer TEXT, 
                      topic TEXT, 
                      description TEXT, 
                      link TEXT, 
                      date TEXT, 
                      direction TEXT)''')
        conn.commit()
        logger.info("Таблица lectures инициализирована")
    except sqlite3.Error as e:
        logger.error(f"Ошибка инициализации базы данных: {e}")
    finally:
        conn.close()

def get_lectures(school=None, direction=None):
    """Получение списка лекций из базы schedule.db."""
    try:
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        
        if school and direction:
            c.execute("SELECT * FROM lectures WHERE school = ? AND direction = ?", (school, direction))
        elif school:
            c.execute("SELECT * FROM lectures WHERE school = ?", (school,))
        else:
            c.execute("SELECT * FROM lectures")
        
        lectures = c.fetchall()
        logger.info(f"Получено {len(lectures)} лекций из базы. Параметры: school={school}, direction={direction}")
        logger.debug(f"Лекции: {lectures}")
        
        return lectures
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении лекций: {e}")
        return []
    finally:
        conn.close()

def get_lectures_for_week(school=None, direction=None):
    """Получение лекций на текущую неделю."""
    try:
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        
        today = datetime.now().date()
        week_later = today + timedelta(days=7)
        
        if school and direction:
            c.execute("SELECT * FROM lectures WHERE school = ? AND direction = ? AND date BETWEEN ? AND ?",
                      (school, direction, today.strftime('%Y-%m-%d'), week_later.strftime('%Y-%m-%d')))
        elif school:
            c.execute("SELECT * FROM lectures WHERE school = ? AND date BETWEEN ? AND ?",
                      (school, today.strftime('%Y-%m-%d'), week_later.strftime('%Y-%m-%d')))
        else:
            c.execute("SELECT * FROM lectures WHERE date BETWEEN ? AND ?",
                      (today.strftime('%Y-%m-%d'), week_later.strftime('%Y-%m-%d')))
        
        lectures = c.fetchall()
        logger.info(f"Получено {len(lectures)} лекций на неделю. Параметры: school={school}, direction={direction}")
        logger.debug(f"Лекции на неделю: {lectures}")
        
        return lectures
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении лекций на неделю: {e}")
        return []
    finally:
        conn.close()

def get_lectures_for_day(school=None, direction=None):
    """Получение лекций на текущий день."""
    try:
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        
        today = datetime.now().date().strftime('%Y-%m-%d')
        
        if school and direction:
            c.execute("SELECT * FROM lectures WHERE school = ? AND direction = ? AND date = ?",
                      (school, direction, today))
        elif school:
            c.execute("SELECT * FROM lectures WHERE school = ? AND date = ?",
                      (school, today))
        else:
            c.execute("SELECT * FROM lectures WHERE date = ?",
                      (today,))
        
        lectures = c.fetchall()
        logger.info(f"Получено {len(lectures)} лекций на текущий день. Параметры: school={school}, direction={direction}")
        logger.debug(f"Лекции на день: {lectures}")
        
        return lectures
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении лекций на день: {e}")
        return []
    finally:
        conn.close()

def get_unpaired_students(pair_type, school=None, direction=None):
    """Получение списка непарных студентов для Random Coffee или Mock Interview."""
    try:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        
        if school and direction:
            c.execute("SELECT username, school, direction FROM unpaired_students WHERE type = ? AND school = ? AND direction = ?",
                      (pair_type, school, direction))
        elif school:
            c.execute("SELECT username, school, direction FROM unpaired_students WHERE type = ? AND school = ?",
                      (pair_type, school))
        else:
            c.execute("SELECT username, school, direction FROM unpaired_students WHERE type = ?",
                      (pair_type,))
        
        students = c.fetchall()
        logger.info(f"Получено {len(students)} непарных студентов для {pair_type}. Параметры: school={school}, direction={direction}")
        logger.debug(f"Непарные студенты: {students}")
        
        return students
    except sqlite3.Error as e:
        logger.error(f"Ошибка при получении непарных студентов: {e}")
        return []
    finally:
        conn.close()

def add_unpaired_student(username, pair_type, school, direction):
    """Добавление студента в список непарных."""
    try:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO unpaired_students (username, type, school, direction) VALUES (?, ?, ?, ?)",
                  (username, pair_type, school, direction))
        conn.commit()
        logger.info(f"Добавлен непарный студент: {username}, type={pair_type}, school={school}, direction={direction}")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при добавлении непарного студента {username}: {e}")
    finally:
        conn.close()

def clear_unpaired_students(pair_type):
    """Очистка списка непарных студентов для указанного типа."""
    try:
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("DELETE FROM unpaired_students WHERE type = ?", (pair_type,))
        conn.commit()
        logger.info(f"Список непарных студентов для {pair_type} очищен")
    except sqlite3.Error as e:
        logger.error(f"Ошибка при очистке непарных студентов для {pair_type}: {e}")
    finally:
        conn.close()