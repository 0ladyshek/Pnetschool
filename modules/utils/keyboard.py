from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

async def keyboard_back(data: str = "menu"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('🔙', callback_data=data))
    return keyboard

async def keyboard_accounts(accounts: list):
    keyboard = InlineKeyboardMarkup()
    for account in accounts:
        keyboard.add(InlineKeyboardButton(account[0], callback_data=f"account|{account[0]}"))
    keyboard.add(InlineKeyboardButton(f"➕Добавить аккаунт", callback_data="add_account"))
    return keyboard

async def keyboard_classes(classes: list, data: str, back: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for class_ in classes:
        keyboard.insert(InlineKeyboardButton(class_['name'], callback_data=f"class|{data}|{class_['id']}"))
    keyboard.row(InlineKeyboardButton(f"🔙", callback_data=f"{back}"))
    return keyboard

async def keyboard_teachers(teachers: dict, data: str, back: str):
    keyboard = InlineKeyboardMarkup()
    for id, name in teachers.items():
        keyboard.add(InlineKeyboardButton(name, callback_data=f"teacher|{data}|{id}"))
    keyboard.add(InlineKeyboardButton("🔙", callback_data=back))
    return keyboard

async def keyboard_settings(notification_mark: int, notification_auth: int):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(f"{'✅' if notification_mark else '❌'}Уведомления о оценках", callback_data=f"settings|notification_mark|{notification_mark}"))
    keyboard.add(InlineKeyboardButton(f"{'✅' if notification_auth else '❌'}Уведомления об авторизациях", callback_data=f"settings|notification_auth|{notification_auth}"))
    keyboard.add(InlineKeyboardButton(f"🔙", callback_data="menu"))
    return keyboard

keyboard_menu = InlineKeyboardMarkup()
keyboard_menu.add(InlineKeyboardButton(f"📕Расписание", callback_data="schedule"), InlineKeyboardButton(f"📖Домашнее задание", callback_data="homework"))
keyboard_menu.add(InlineKeyboardButton(f"5️⃣Оценки", callback_data="marks"), InlineKeyboardButton(f"📆События", callback_data="events"))
keyboard_menu.add(InlineKeyboardButton(f"ℹ️Информация", callback_data="info"), InlineKeyboardButton(f"⚙️Настройки", callback_data="settings"))
keyboard_menu.add(InlineKeyboardButton(f"🔙Выйти", callback_data="exit"))

keyboard_school = InlineKeyboardMarkup()
keyboard_school.add(InlineKeyboardButton("🔎Найти школу", switch_inline_query_current_chat=""))
keyboard_school.add(InlineKeyboardButton(f"🔙", callback_data="register|get_password"))

keyboard_schedule = InlineKeyboardMarkup()
keyboard_schedule.add(InlineKeyboardButton(f"⏪Вчера", callback_data="schedule|-1"), InlineKeyboardButton(f"⏺️Сегодня", callback_data="schedule|0"), InlineKeyboardButton(f"⏩️Завтра", callback_data="schedule|1"))
keyboard_schedule.add(InlineKeyboardButton(f"↔️Неделя", callback_data="schedule|week"))
keyboard_schedule.add(InlineKeyboardButton(f"📖Выбрать класс", callback_data="class_schedule"), InlineKeyboardButton(f"🧑‍🏫Выбрать учителя", callback_data="teacher_schedule"))
keyboard_schedule.add(InlineKeyboardButton(f"🔙", callback_data="menu"))

keyboard_homework = InlineKeyboardMarkup()
keyboard_homework.add(InlineKeyboardButton(f"⏪Вчера", callback_data="homework|-1"), InlineKeyboardButton(f"⏺️Сегодня", callback_data="homework|0"), InlineKeyboardButton(f"⏩️Завтра", callback_data="homework|1"))
keyboard_homework.add(InlineKeyboardButton(f"↔️Неделя", callback_data="homework|week"))
keyboard_homework.add(InlineKeyboardButton(f"🔙", callback_data="menu"))

keyboard_marks = InlineKeyboardMarkup()
keyboard_marks.add(InlineKeyboardButton(f'🔟Расширенная', callback_data="advanced_marks"))
keyboard_marks.add(InlineKeyboardButton(f"🔃Общая", callback_data="report_marks"))
keyboard_marks.add(InlineKeyboardButton(f"🔙", callback_data="menu"))

keyboard_events = InlineKeyboardMarkup()
keyboard_events.add(InlineKeyboardButton(f"📅Дни рождения", callback_data="birthday"))
keyboard_events.add(InlineKeyboardButton(f"🎈Праздники", callback_data="holidays"))
keyboard_events.add(InlineKeyboardButton(f"📣Объявления", callback_data="ads"))
keyboard_events.add(InlineKeyboardButton(f"🔙", callback_data="menu"))

keyboard_birthdays = InlineKeyboardMarkup()
keyboard_birthdays.add(InlineKeyboardButton(f"⏪Предыдущий", callback_data="birthdays|-1"), InlineKeyboardButton(f"⏺️Текущий", callback_data="birthdays|0"), InlineKeyboardButton(f"⏩️Следующий", callback_data="birthdays|1"))
keyboard_birthdays.add(InlineKeyboardButton(f"🔟Год", callback_data="birthdays|year"))
keyboard_birthdays.add(InlineKeyboardButton(f"🔙", callback_data="events"))

keyboard_info = InlineKeyboardMarkup()
keyboard_info.add(InlineKeyboardButton(f"👤Аккаунт", callback_data="info_student"), InlineKeyboardButton(F"🏫Школа", callback_data="info_school"))
keyboard_info.add(InlineKeyboardButton(f"🌐Активные сессии", callback_data="info_sessions"), InlineKeyboardButton(f"👥Пользователи", callback_data="info_users"))
keyboard_info.add(InlineKeyboardButton(f"🔙", callback_data="menu"))

keyboard_info_school = InlineKeyboardMarkup()
keyboard_info_school.add(InlineKeyboardButton(f"🏫Полная информация", callback_data="info_school_full"))
keyboard_info_school.add(InlineKeyboardButton(f"🔙", callback_data="info"))

keyboard_users = InlineKeyboardMarkup()
keyboard_users.add(InlineKeyboardButton(f"🧑‍🎓Ученики", callback_data="students"), InlineKeyboardButton(f"🧑‍🏫Учитель", callback_data="teachers"))
keyboard_users.add(InlineKeyboardButton(f"🏫Класс", callback_data="class_info"))
keyboard_users.add(InlineKeyboardButton(f"🔙", callback_data="info"))