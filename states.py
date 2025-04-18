from aiogram.fsm.state import State, StatesGroup

class StudentMenu(StatesGroup):
    select_school = State()
    select_direction = State()
    main = State()

class AdminMode(StatesGroup):
    main = State()
    add_lecture_school = State()
    add_lecture_direction = State()
    add_lecture_lecturer = State()
    add_lecture_topic = State()
    add_lecture_description = State()
    add_lecture_link = State()
    add_lecture_date = State()
    delete_lecture = State()
    select_lecture = State()
    select_edit_field = State()
    update_lecture_field = State()
    select_alert_school = State()
    send_alert = State()
    form_pairs = State()