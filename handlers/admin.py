import logging
import sqlite3
from datetime import datetime
from aiogram import Dispatcher
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove, KeyboardButton, ReplyKeyboardMarkup
from states import AdminMode, StudentMenu
from utils.keyboards import get_schools_keyboard, get_admin_menu_keyboard, get_form_pairs_keyboard, get_edit_lecture_keyboard, get_direction_keyboard, get_student_menu_keyboard, get_back_keyboard
from database import get_lectures
from handlers.scheduler import organize_random_coffee, organize_mock_interview

# Настройка логирования
logger = logging.getLogger(__name__)

def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков для админского режима."""
    dp.message.register(activate_admin_mode, lambda message: message.text == "Октавиан Август")
    dp.message.register(admin_menu, StateFilter(AdminMode.main))
    dp.message.register(add_lecture_school, StateFilter(AdminMode.add_lecture_school))
    dp.message.register(add_lecture_direction, StateFilter(AdminMode.add_lecture_direction))
    dp.message.register(add_lecture_lecturer, StateFilter(AdminMode.add_lecture_lecturer))
    dp.message.register(add_lecture_topic, StateFilter(AdminMode.add_lecture_topic))
    dp.message.register(add_lecture_description, StateFilter(AdminMode.add_lecture_description))
    dp.message.register(add_lecture_link, StateFilter(AdminMode.add_lecture_link))
    dp.message.register(add_lecture_date, StateFilter(AdminMode.add_lecture_date))
    dp.message.register(delete_lecture, StateFilter(AdminMode.delete_lecture))
    dp.message.register(select_lecture, StateFilter(AdminMode.select_lecture))
    dp.message.register(select_edit_field, StateFilter(AdminMode.select_edit_field))
    dp.message.register(update_lecture_field, StateFilter(AdminMode.update_lecture_field))
    dp.message.register(select_alert_school, StateFilter(AdminMode.select_alert_school))
    dp.message.register(send_alert, StateFilter(AdminMode.send_alert))
    dp.message.register(form_pairs, StateFilter(AdminMode.form_pairs))
    # Регистрация обработки кнопки "Назад" для всех состояний добавления лекции
    for state in [AdminMode.add_lecture_school, AdminMode.add_lecture_direction, AdminMode.add_lecture_lecturer,
                  AdminMode.add_lecture_topic, AdminMode.add_lecture_description, AdminMode.add_lecture_link,
                  AdminMode.add_lecture_date, AdminMode.delete_lecture, AdminMode.select_lecture,
                  AdminMode.select_edit_field, AdminMode.update_lecture_field]:
        dp.message.register(back_to_admin_menu, StateFilter(state), lambda message: message.text == "Назад")

async def activate_admin_mode(message: Message, state: FSMContext):
    """Активация админского режима по кодовой фразе."""
    username = message.from_user.username or str(message.from_user.id)
    current_state = await state.get_state()
    logger.info(f"Попытка активации админского режима для {username}, текущий state: {current_state}, текст: {message.text}")
    
    # Сохраняем текущее значение school перед изменением
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    c.execute("SELECT school FROM students WHERE username = ?", (username,))
    result = c.fetchone()
    
    if result:
        await state.update_data(original_school=result[0])
        c.execute("UPDATE students SET school = ? WHERE username = ?", ('АДМИН', username))
        conn.commit()
        logger.info(f"Поле school для {username} установлено в АДМИН, оригинальная школа: {result[0]}")
    else:
        c.execute("INSERT INTO students (username, school, direction, random_coffee, mock_interview) VALUES (?, ?, ?, ?, ?)",
                  (username, 'АДМИН', None, 0, 0))
        conn.commit()
        await state.update_data(original_school=None)
        logger.info(f"Создан новый пользователь {username} с school=АДМИН")
    
    conn.close()
    
    await message.reply("Админский режим активирован. Выберите действие:", reply_markup=get_admin_menu_keyboard())
    await state.set_state(AdminMode.main)
    logger.info(f"Админский режим успешно активирован для {username}")

async def back_to_admin_menu(message: Message, state: FSMContext):
    """Обработка кнопки 'Назад' для возврата в меню админки."""
    await message.reply("Выберите действие:", reply_markup=get_admin_menu_keyboard())
    await state.set_state(AdminMode.main)
    logger.info(f"Пользователь {message.from_user.id} вернулся в меню админки")

async def admin_menu(message: Message, state: FSMContext):
    """Обработка выбора действия в админском меню."""
    choice = message.text.strip()
    logger.info(f"Админский выбор: {choice} от {message.from_user.id}")

    if choice == "Добавить лекцию":
        await message.reply("Выберите школу для лекции:", reply_markup=get_schools_keyboard(include_back=True))
        await state.set_state(AdminMode.add_lecture_school)
        logger.info(f"Переход к добавлению лекции")
    elif choice == "Удалить лекцию":
        lectures = get_lectures()
        if not lectures:
            await message.reply("Лекции отсутствуют.", reply_markup=get_admin_menu_keyboard())
            logger.info("Лекции для удаления отсутствуют")
            return
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=str(i))] for i in range(len(lectures))] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.reply("\n".join([f"{i}: {l[1]}, {l[2]}, {l[6]}, {l[7] or 'Без направления'}" for i, l in enumerate(lectures)]),
                           reply_markup=keyboard)
        await state.set_state(AdminMode.delete_lecture)
        logger.info(f"Переход к удалению лекции")
    elif choice == "Изменить лекцию":
        lectures = get_lectures()
        if not lectures:
            await message.reply("Лекции отсутствуют.", reply_markup=get_admin_menu_keyboard())
            logger.info("Лекции для изменения отсутствуют")
            return
        keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=str(i))] for i in range(len(lectures))] + [[KeyboardButton(text="Назад")]],
            resize_keyboard=True
        )
        await message.reply("\n".join([f"{i}: {l[1]}, {l[2]}, {l[6]}, {l[7] or 'Без направления'}" for i, l in enumerate(lectures)]),
                           reply_markup=keyboard)
        await state.set_state(AdminMode.select_lecture)
        logger.info(f"Переход к изменению лекции")
    elif choice == "Отправить оповещение":
        schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ', 'Все школы']
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text=schools[0]), KeyboardButton(text=schools[1])],
                [KeyboardButton(text=schools[2]), KeyboardButton(text=schools[3])],
                [KeyboardButton(text=schools[4]), KeyboardButton(text=schools[5])],
                [KeyboardButton(text=schools[6])]
            ],
            resize_keyboard=True
        )
        await message.reply("Выберите школу для оповещения:", reply_markup=keyboard)
        await state.set_state(AdminMode.select_alert_school)
        logger.info(f"Переход к отправке оповещения")
    elif choice == "Сформировать пары":
        await message.reply("Выберите тип пар:", reply_markup=get_form_pairs_keyboard())
        await state.set_state(AdminMode.form_pairs)
        logger.info(f"Переход к формированию пар")
    elif choice == "Выйти из админки":
        data = await state.get_data()
        original_school = data.get('original_school')
        username = message.from_user.username or str(message.from_user.id)
        
        # Восстанавливаем оригинальную школу
        conn = sqlite3.connect('students.db')
        c = conn.cursor()
        if original_school:
            c.execute("UPDATE students SET school = ? WHERE username = ?", (original_school, username))
            conn.commit()
            logger.info(f"Восстановлена школа {original_school} для {username}")
        else:
            c.execute("DELETE FROM students WHERE username = ?", (username,))
            conn.commit()
            logger.info(f"Удалена запись для {username}, так как не было оригинальной школы")
        conn.close()
        
        await message.reply("Админский режим отключен.", reply_markup=get_student_menu_keyboard())
        await state.clear()
        logger.info(f"Пользователь {message.from_user.id} вышел из админки")
    else:
        await message.reply("Пожалуйста, выберите действие из меню.", reply_markup=get_admin_menu_keyboard())
        logger.warning(f"Некорректный выбор в админке: {choice}")

async def add_lecture_school(message: Message, state: FSMContext):
    """Обработка выбора школы для новой лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    school = message.text.strip().upper()
    valid_schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ']
    if school not in valid_schools:
        await message.reply("Пожалуйста, выберите школу из предложенных.", reply_markup=get_schools_keyboard(include_back=True))
        logger.warning(f"Некорректная школа для лекции: {school}")
        return
    
    await state.update_data(school=school)
    
    if school in ['ШБР', 'ШМР']:
        await message.reply("Выберите направление:", reply_markup=get_direction_keyboard(school, include_back=True))
        await state.set_state(AdminMode.add_lecture_direction)
        logger.info(f"Переход к выбору направления для школы {school}")
    else:
        await state.update_data(direction=None)
        await message.reply("Введите имя лектора:", reply_markup=get_back_keyboard())
        await state.set_state(AdminMode.add_lecture_lecturer)
        logger.info(f"Переход к вводу лектора для школы {school}")

async def add_lecture_direction(message: Message, state: FSMContext):
    """Обработка выбора направления для лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    direction = message.text.strip()
    data = await state.get_data()
    school = data['school']
    
    valid_directions = {
        'ШБР': ['Java', 'C++', 'Python'],
        'ШМР': ['Android', 'iOS', 'Flutter']
    }
    
    if direction not in valid_directions[school]:
        await message.reply("Пожалуйста, выберите направление из предложенных.", reply_markup=get_direction_keyboard(school, include_back=True))
        logger.warning(f"Некорректное направление: {direction} для школы {school}")
        return
    
    await state.update_data(direction=direction)
    await message.reply("Введите имя лектора:", reply_markup=get_back_keyboard())
    await state.set_state(AdminMode.add_lecture_lecturer)
    logger.info(f"Выбрано направление: {direction} для школы {school}")

async def add_lecture_lecturer(message: Message, state: FSMContext):
    """Обработка ввода имени лектора."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    lecturer = message.text.strip()
    await state.update_data(lecturer=lecturer)
    await message.reply("Введите тему лекции:", reply_markup=get_back_keyboard())
    await state.set_state(AdminMode.add_lecture_topic)
    logger.info(f"Лектор введён: {lecturer}")

async def add_lecture_topic(message: Message, state: FSMContext):
    """Обработка ввода темы лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    topic = message.text.strip()
    await state.update_data(topic=topic)
    await message.reply("Введите описание лекции:", reply_markup=get_back_keyboard())
    await state.set_state(AdminMode.add_lecture_description)
    logger.info(f"Тема лекции введена: {topic}")

async def add_lecture_description(message: Message, state: FSMContext):
    """Обработка ввода описания лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    description = message.text.strip()
    await state.update_data(description=description)
    await message.reply("Введите ссылку на лекцию:", reply_markup=get_back_keyboard())
    await state.set_state(AdminMode.add_lecture_link)
    logger.info(f"Описание лекции введено")

async def add_lecture_link(message: Message, state: FSMContext):
    """Обработка ввода ссылки на лекцию."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    link = message.text.strip()
    await state.update_data(link=link)
    await message.reply("Введите дату лекции (YYYY-MM-DD):", reply_markup=get_back_keyboard())
    await state.set_state(AdminMode.add_lecture_date)
    logger.info(f"Ссылка на лекцию введена")

async def add_lecture_date(message: Message, state: FSMContext):
    """Обработка ввода даты лекции и сохранение лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    date = message.text.strip()
    try:
        datetime.strptime(date, '%Y-%m-%d')
    except ValueError:
        await message.reply("Некорректный формат даты. Введите в формате YYYY-MM-DD.", reply_markup=get_back_keyboard())
        logger.warning(f"Некорректный формат даты: {date}")
        return

    data = await state.get_data()
    school = data['school']
    lecturer = data['lecturer']
    topic = data['topic']
    description = data['description']
    link = data['link']
    direction = data.get('direction')
    
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute("INSERT INTO lectures (school, lecturer, topic, description, link, date, direction) VALUES (?, ?, ?, ?, ?, ?, ?)",
              (school, lecturer, topic, description, link, date, direction))
    conn.commit()
    conn.close()
    await message.reply("Лекция добавлена!", reply_markup=get_admin_menu_keyboard())
    await state.set_state(AdminMode.main)
    logger.info(f"Добавлена лекция: {school}, {topic}, {date}, направление: {direction}")

async def delete_lecture(message: Message, state: FSMContext):
    """Обработка удаления лекции."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    try:
        index = int(message.text)
        lectures = get_lectures()
        if index < 0 or index >= len(lectures):
            await message.reply("Некорректный номер лекции.", reply_markup=get_back_keyboard())
            logger.warning(f"Некорректный номер лекции: {index}")
            return
        
        lecture_id = lectures[index][0]
        conn = sqlite3.connect('schedule.db')
        c = conn.cursor()
        c.execute("DELETE FROM lectures WHERE id = ?", (lecture_id,))
        conn.commit()
        conn.close()
        await message.reply("Лекция удалена!", reply_markup=get_admin_menu_keyboard())
        logger.info(f"Удалена лекция с ID: {lecture_id}")
        await state.set_state(AdminMode.main)
    except ValueError:
        await message.reply("Введите номер лекции.", reply_markup=get_back_keyboard())
        logger.warning(f"Некорректный ввод номера лекции: {message.text}")
        return

async def select_lecture(message: Message, state: FSMContext):
    """Обработка выбора лекции для редактирования."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    try:
        index = int(message.text)
        lectures = get_lectures()
        if index < 0 or index >= len(lectures):
            await message.reply("Некорректный номер лекции.", reply_markup=get_back_keyboard())
            logger.warning(f"Некорректный номер лекции: {index}")
            return
        
        lecture = lectures[index]
        await state.update_data(lecture_id=lecture[0], lecture_data=lecture)
        await message.reply(
            f"Выбрана лекция: {lecture[1]}, {lecture[2]}, {lecture[6]}, {lecture[7] or 'Без направления'}\nВыберите, что изменить:",
            reply_markup=get_edit_lecture_keyboard(include_back=True)
        )
        await state.set_state(AdminMode.select_edit_field)
        logger.info(f"Выбрана лекция для редактирования: ID {lecture[0]}")
    except ValueError:
        await message.reply("Введите номер лекции.", reply_markup=get_back_keyboard())
        logger.warning(f"Некорректный ввод номера лекции: {message.text}")
        return

async def select_edit_field(message: Message, state: FSMContext):
    """Обработка выбора поля для редактирования."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    field = message.text.strip()
    valid_fields = ['Школа', 'Лектор', 'Тема', 'Описание', 'Ссылка', 'Дата', 'Направление']
    
    if field not in valid_fields:
        await message.reply("Пожалуйста, выберите поле из предложенных.", reply_markup=get_edit_lecture_keyboard(include_back=True))
        logger.warning(f"Некорректное поле для редактирования: {field}")
        return
    
    field_map = {
        'Школа': 'school',
        'Лектор': 'lecturer',
        'Тема': 'topic',
        'Описание': 'description',
        'Ссылка': 'link',
        'Дата': 'date',
        'Направление': 'direction'
    }
    
    await state.update_data(edit_field=field_map[field])
    
    if field == 'Школа':
        await message.reply("Выберите новую школу:", reply_markup=get_schools_keyboard(include_back=True))
    elif field == 'Направление':
        data = await state.get_data()
        lecture = data['lecture_data']
        school = lecture[1]  # Поле school в лекции
        if school in ['ШБР', 'ШМР']:
            await message.reply("Выберите новое направление:", reply_markup=get_direction_keyboard(school, include_back=True))
        else:
            await message.reply("Направление не требуется для этой школы. Введите 'Нет' или оставьте пустым:", reply_markup=get_back_keyboard())
    elif field == 'Дата':
        await message.reply("Введите новую дату (YYYY-MM-DD):", reply_markup=get_back_keyboard())
    else:
        await message.reply(f"Введите новое значение для поля '{field}':", reply_markup=get_back_keyboard())
    
    await state.set_state(AdminMode.update_lecture_field)
    logger.info(f"Выбрано поле для редактирования: {field}")

async def update_lecture_field(message: Message, state: FSMContext):
    """Обработка ввода нового значения для выбранного поля."""
    if message.text == "Назад":
        await back_to_admin_menu(message, state)
        return
    
    new_value = message.text.strip()
    data = await state.get_data()
    lecture_id = data['lecture_id']
    field = data['edit_field']
    
    # Валидация
    if field == 'school':
        valid_schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ']
        new_value = new_value.upper()
        if new_value not in valid_schools:
            await message.reply("Некорректная школа. Выберите из предложенных:", reply_markup=get_schools_keyboard(include_back=True))
            logger.warning(f"Некорректная школа: {new_value}")
            return
    elif field == 'direction':
        lecture = data['lecture_data']
        school = lecture[1]
        valid_directions = {
            'ШБР': ['Java', 'C++', 'Python'],
            'ШМР': ['Android', 'iOS', 'Flutter']
        }
        if school in ['ШБР', 'ШМР']:
            if new_value not in valid_directions[school]:
                await message.reply("Некорректное направление. Выберите из предложенных:", reply_markup=get_direction_keyboard(school, include_back=True))
                logger.warning(f"Некорректное направление: {new_value} для школы {school}")
                return
        else:
            new_value = None if new_value.lower() in ['нет', ''] else new_value
    elif field == 'date':
        try:
            datetime.strptime(new_value, '%Y-%m-%d')
        except ValueError:
            await message.reply("Некорректный формат даты. Введите в формате YYYY-MM-DD.", reply_markup=get_back_keyboard())
            logger.warning(f"Некорректный формат даты: {new_value}")
            return
    
    # Обновление поля в базе данных
    conn = sqlite3.connect('schedule.db')
    c = conn.cursor()
    c.execute(f"UPDATE lectures SET {field} = ? WHERE id = ?", (new_value, lecture_id))
    conn.commit()
    conn.close()
    
    await message.reply(f"Поле '{field}' обновлено!", reply_markup=get_admin_menu_keyboard())
    await state.set_state(AdminMode.main)
    logger.info(f"Обновлено поле '{field}' для лекции ID {lecture_id}: {new_value}")

async def select_alert_school(message: Message, state: FSMContext):
    """Обработка выбора школы для оповещения."""
    school = message.text.strip().upper()
    valid_schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ', 'ВСЕ ШКОЛЫ']
    if school not in valid_schools:
        await message.reply("Пожалуйста, выберите школу из предложенных.")
        logger.warning(f"Некорректная школа для оповещения: {school}")
        return
    
    await state.update_data(alert_school=school)
    await message.reply("Введите текст оповещения:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(AdminMode.send_alert)
    logger.info(f"Выбрана школа для оповещения: {school}")

async def send_alert(message: Message, state: FSMContext):
    """Обработка отправки оповещения."""
    alert_text = message.text.strip()
    data = await state.get_data()
    school = data['alert_school']
    
    conn = sqlite3.connect('students.db')
    c = conn.cursor()
    if school == 'ВСЕ ШКОЛЫ':
        c.execute("SELECT username FROM students")
    else:
        c.execute("SELECT username FROM students WHERE school = ?", (school,))
    students = c.fetchall()
    conn.close()

    for student in students:
        username = student[0]
        try:
            await message.bot.send_message(
                chat_id=username,
                text=f"Экстренное оповещение!\n{alert_text}"
            )
            logger.info(f"Оповещение отправлено {username}")
        except Exception as e:
            logger.error(f"Ошибка отправки оповещения {username}: {e}")

    await message.reply(f"Оповещение отправлено студентам {'всех школ' if school == 'ВСЕ ШКОЛЫ' else school}",
                       reply_markup=get_admin_menu_keyboard())
    await state.set_state(AdminMode.main)
    logger.info(f"Оповещение отправлено для школы {school}")

async def form_pairs(message: Message, state: FSMContext):
    """Обработка формирования пар для Random Coffee или Mock Interview."""
    choice = message.text.strip()
    logger.info(f"Админ выбрал формирование пар: {choice}")

    if choice == "Random Coffee":
        await organize_random_coffee(message.bot)
        await message.reply("Пары для Random Coffee сформированы и уведомления отправлены!",
                           reply_markup=get_admin_menu_keyboard())
        logger.info("Пары для Random Coffee сформированы")
    elif choice == "Mock Interview":
        await organize_mock_interview(message.bot)
        await message.reply("Пары для Mock Interview сформированы и уведомления отправлены!",
                           reply_markup=get_admin_menu_keyboard())
        logger.info("Пары для Mock Interview сформированы")
    elif choice == "Назад":
        await message.reply("Выберите действие:", reply_markup=get_admin_menu_keyboard())
        await state.set_state(AdminMode.main)
        logger.info("Возврат в главное меню админки")
        return
    else:
        await message.reply("Пожалуйста, выберите тип пар из меню.", reply_markup=get_form_pairs_keyboard())
        logger.warning(f"Некорректный выбор типа пар: {choice}")
    
    await state.set_state(AdminMode.main)