import logging
import sqlite3
from aiogram import Dispatcher
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from states import StudentMenu
from utils.keyboards import get_schools_keyboard, get_direction_keyboard, get_student_menu_keyboard
from database import get_lectures, get_lectures_for_week

# Настройка логирования
logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков для регистрации и меню студента."""
    dp.message.register(start, CommandStart())
    dp.message.register(select_school, StateFilter(StudentMenu.select_school))
    dp.message.register(select_direction, StateFilter(StudentMenu.select_direction))
    dp.message.register(student_menu, StateFilter(StudentMenu.main))

async def start(message: Message, state: FSMContext):
    """Обработка команды /start."""
    username = message.from_user.username or str(message.from_user.id)
    logger.info(f"Команда /start от {username}")
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT school, direction FROM students WHERE username = ?", (username,))
    result = c.fetchone()
    
    if result:
        school, direction = result
        await message.reply(f"Вы уже зарегистрированы: {school}{', ' + direction if direction else ''}.",
                           reply_markup=get_student_menu_keyboard())
        await state.set_state(StudentMenu.main)
        logger.info(f"Пользователь {username} уже зарегистрирован: {school}, {direction}")
    else:
        await message.reply("Выберите школу:", reply_markup=get_schools_keyboard())
        await state.set_state(StudentMenu.select_school)
        logger.info(f"Начало регистрации для {username}")
    
    conn.close()

async def select_school(message: Message, state: FSMContext):
    """Обработка выбора школы."""
    school = message.text.strip().upper()
    valid_schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ']
    
    if school not in valid_schools:
        await message.reply("Пожалуйста, выберите школу из предложенных.", reply_markup=get_schools_keyboard())
        logger.warning(f"Некорректная школа: {school}")
        return
    
    await state.update_data(school=school)
    
    if school in ['ШБР', 'ШМР']:
        await message.reply("Выберите направление:", reply_markup=get_direction_keyboard(school))
        await state.set_state(StudentMenu.select_direction)
        logger.info(f"Переход к выбору направления для школы {school}")
    else:
        await state.update_data(direction=None)
        await complete_registration(message, state)

async def select_direction(message: Message, state: FSMContext):
    """Обработка выбора направления."""
    direction = message.text.strip()
    data = await state.get_data()
    school = data['school']
    
    valid_directions = {
        'ШБР': ['Java', 'C++', 'Python'],
        'ШМР': ['Android', 'iOS', 'Flutter']
    }
    
    if direction not in valid_directions[school]:
        await message.reply("Пожалуйста, выберите направление из предложенных.", reply_markup=get_direction_keyboard(school))
        logger.warning(f"Некорректное направление: {direction} для школы {school}")
        return
    
    await state.update_data(direction=direction)
    await complete_registration(message, state)

async def complete_registration(message: Message, state: FSMContext):
    """Завершение регистрации."""
    data = await state.get_data()
    school = data['school']
    direction = data.get('direction')
    username = message.from_user.username or str(message.from_user.id)
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO students (username, school, direction, random_coffee, mock_interview) VALUES (?, ?, ?, ?, ?)",
              (username, school, direction, 0, 0))
    conn.commit()
    conn.close()
    
    await message.reply(f"Регистрация завершена! Школа: {school}{', направление: ' + direction if direction else ''}.",
                       reply_markup=get_student_menu_keyboard())
    await state.set_state(StudentMenu.main)
    logger.info(f"Регистрация завершена для {username}: {school}, {direction}")

async def student_menu(message: Message, state: FSMContext):
    """Обработка выбора в меню студента."""
    choice = message.text.strip()
    username = message.from_user.username or str(message.from_user.id)
    logger.info(f"Выбор в меню студента: {choice} от {username}")
    
    if choice == "Октавиан Август":
        logger.info(f"Сообщение 'Октавиан Август' от {username} пропущено для обработки админкой")
        return
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT school, direction, random_coffee, mock_interview FROM students WHERE username = ?", (username,))
    result = c.fetchone()
    conn.close()
    
    if not result:
        await message.reply("Вы не зарегистрированы. Начните с /start.", reply_markup=ReplyKeyboardRemove())
        await state.clear()
        logger.warning(f"Пользователь {username} не зарегистрирован")
        return
    
    school, direction, random_coffee, mock_interview = result
    
    if choice == "Посмотреть лекции":
        lectures = get_lectures(school, direction)
        if not lectures:
            await message.reply("Лекции отсутствуют.", reply_markup=get_student_menu_keyboard())
            logger.info(f"Лекции отсутствуют для {school}, {direction}")
            return
        lecture_list = "\n".join([f"{l[2]} ({l[1]}, {l[6]}): {l[4]}\n{l[5]}" for l in lectures])
        await message.reply(lecture_list, reply_markup=get_student_menu_keyboard())
        logger.info(f"Показан список лекций для {username}")
    elif choice == "Лекции на неделю":
        lectures = get_lectures_for_week(school, direction)
        if not lectures:
            await message.reply("Лекции на этой неделе отсутствуют.", reply_markup=get_student_menu_keyboard())
            logger.info(f"Лекции на неделю отсутствуют для {school}, {direction}")
            return
        lecture_list = "\n".join([f"{l[2]} ({l[1]}, {l[6]}): {l[4]}\n{l[5]}" for l in lectures])
        await message.reply(lecture_list, reply_markup=get_student_menu_keyboard())
        logger.info(f"Показан список лекций на неделю для {username}")
    elif choice == "Random Coffee":
        new_status = 0 if random_coffee else 1
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("UPDATE students SET random_coffee = ? WHERE username = ?", (new_status, username))
        conn.commit()
        conn.close()
        action = "записаны на" if new_status else "отписаны от"
        await message.reply(f"Вы {action} Random Coffee!", reply_markup=get_student_menu_keyboard())
        logger.info(f"Пользователь {username} {action} Random Coffee")
    elif choice == "Mock Interview":
        new_status = 0 if mock_interview else 1
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        c.execute("UPDATE students SET mock_interview = ? WHERE username = ?", (new_status, username))
        conn.commit()
        conn.close()
        action = "записаны на" if new_status else "отписаны от"
        await message.reply(f"Вы {action} Mock Interview!", reply_markup=get_student_menu_keyboard())
        logger.info(f"Пользователь {username} {action} Mock Interview")
    else:
        await message.reply("Пожалуйста, выберите действие из меню.", reply_markup=get_student_menu_keyboard())
        logger.warning(f"Некорректный выбор в меню: {choice} от {username}")