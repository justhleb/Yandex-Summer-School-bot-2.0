from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_schools_keyboard(include_back=False):
    """Клавиатура для выбора школы."""
    schools = ['ШАР', 'ШМР', 'ШБР', 'ШРИ', 'ШОК', 'ШМЯ']
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=schools[0]), KeyboardButton(text=schools[1])],
            [KeyboardButton(text=schools[2]), KeyboardButton(text=schools[3])],
            [KeyboardButton(text=schools[4]), KeyboardButton(text=schools[5])]
        ] + ([[KeyboardButton(text="Назад")]] if include_back else []),
        resize_keyboard=True
    )
    return keyboard

def get_direction_keyboard(school, include_back=False):
    """Клавиатура для выбора направления."""
    directions = {
        'ШБР': ['Java', 'C++', 'Python'],
        'ШМР': ['Android', 'iOS', 'Flutter']
    }
    direction_list = directions.get(school, [])
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=d)] for d in direction_list] + ([[KeyboardButton(text="Назад")]] if include_back else []),
        resize_keyboard=True
    )
    return keyboard

def get_admin_menu_keyboard():
    """Клавиатура главного меню админки."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Добавить лекцию"), KeyboardButton(text="Удалить лекцию")],
            [KeyboardButton(text="Изменить лекцию"), KeyboardButton(text="Отправить оповещение")],
            [KeyboardButton(text="Сформировать пары"), KeyboardButton(text="Выйти из админки")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_form_pairs_keyboard():
    """Клавиатура для выбора типа пар."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Random Coffee"), KeyboardButton(text="Mock Interview")],
            [KeyboardButton(text="Назад")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_edit_lecture_keyboard(include_back=False):
    """Клавиатура для выбора поля редактирования лекции."""
    fields = ['Школа', 'Лектор', 'Тема', 'Описание', 'Ссылка', 'Дата', 'Направление']
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=f)] for f in fields] + ([[KeyboardButton(text="Назад")]] if include_back else []),
        resize_keyboard=True
    )
    return keyboard

def get_student_menu_keyboard():
    """Клавиатура меню студента."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Посмотреть лекции"), KeyboardButton(text="Лекции на неделю")],
            [KeyboardButton(text="Random Coffee"), KeyboardButton(text="Mock Interview")]
        ],
        resize_keyboard=True
    )
    return keyboard

def get_back_keyboard():
    """Клавиатура с одной кнопкой 'Назад'."""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Назад")]],
        resize_keyboard=True
    )
    return keyboard