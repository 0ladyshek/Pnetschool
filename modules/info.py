from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from .utils.maria import Maria
from .utils.keyboard import keyboard_back, keyboard_info, keyboard_info_school, keyboard_users, keyboard_classes
from .netschool.netschool import NetSchool
from .utils.other import birthday_to_year, name_param_school, too_long_result, number_to_emoji
from io import StringIO
import re
from datetime import datetime

maria = Maria()

#commands=['info']
async def info(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"ℹ️Выберите раздел", reply_markup=keyboard_info)

#text="info"
async def info_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"ℹ️Выберите раздел", reply_markup=keyboard_info)
    
#text="info_student"
async def info_student(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    settings, photo = await api.settings(True)
    await api.logout()
    
    result = f"👤ФИО: {settings['lastName']} {settings['firstName']} {settings['middleName'] if settings['middleName'] else ''}\n"
    result += f"🔐Логин: {account[1]}\n"
    result += f"🗝Пароль: {account[2]}\n"
    result += f"🎂Дата рождения: {datetime.strptime(settings['birthDate'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}{await birthday_to_year(settings['birthDate'])}\n"
    result += f"🎭Роли: {' '.join(settings['roles'])}\n"
    result += f"☎️Телефон: {settings['mobilePhone']}\n"
    result += f"📧Email: {settings['email']}"
    
    await message.message.delete()
    await message.message.answer_photo(caption=result, photo=photo)
    await message.message.answer(f"✅Готово", reply_markup=keyboard_info)
    
#text="info_school"
async def info_school(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await state.finish()
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    school = await api.school_card()
    await api.logout()
    
    result = f""
    result += f"\n🔖Название: {school['commonInfo']['schoolName']}"
    result += f"\n📜Юр. адрес: {school['contactInfo']['postAddress']}"
    if school['commonInfo']['foundingDate']:
        result += f"\n🗓Дата основания: {re.search('(.*)T00:00:00', school['commonInfo']['foundingDate']).group(1)}"
    result += f"\n✉️E-mail: {school['contactInfo']['email']}"
    result += f"\n💻Сайт: {school['contactInfo']['web']}"
    result += f"\n📞Номер телефона: {school['contactInfo']['phones']}"
    result += f"\n🙍‍♂️Директор (ФИО): {school['managementInfo']['director']}"
    result += f"\n👨‍🏫Зам директора по УВР (ФИО): {school['managementInfo']['principalUVR']}"
    result += f"\n👨‍💻Зам директора по ИТ (ФИО): {school['managementInfo']['principalIT']}"
    result += f"\n👨‍💼Зам директора по АХЧ (ФИО): {school['managementInfo']['principalAHC']}"
    result += f"\n📃ИНН: {school['otherInfo']['inn']}"
    result += f"\n📄Для донатов: {school['bankDetails']['bankScore']}"
    
    await message.message.edit_text(result, reply_markup=keyboard_info_school)
    
#text="info_school_full"
async def info_school_full(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await state.finish()
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    school = await api.school_card()
    await api.logout()
    
    result = ""
    for value in school.values():
        for key, item in value.items():
            if item and name_param_school.get(key):
                if isinstance(item, str):
                    result += f"{name_param_school[key]}: {item}\n"
                elif isinstance(item, list):
                    result += f"{name_param_school[key]}: {' '.join(item)}\n"
                elif isinstance(item, dict):
                    result += f"Местность: {item['locationType']['name']}\n"
    
    result = await too_long_result(result)
    await message.message.delete()
    for i in result:
        await message.message.answer(i)
    await message.message.answer(f"✅Готово", reply_markup=keyboard_info)
    
#text="info_sessions"
async def sessions(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    sessions_list = await api.sessions()
    await api.logout()
    
    result = f"*🌐Активные сессии:*"
    result += f"\n".join([f"{(await number_to_emoji(i))} {session['nickName']}" for i, session in enumerate(sessions_list)])
    
    result = await too_long_result(result)
    
    await message.message.delete()
    for i in result:
        await message.message.answer(i, parse_mode="markdown")
    await message.message.answer("✅Готово", reply_markup=keyboard_info)
    
#text="info_users"
async def info_users(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"👥Выберите категорию", reply_markup=keyboard_users)
    
#text="students"
async def students(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")

    users = []
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    classes = await api.classes()
    for class_ in classes:
        _, students_class = await api.class_info(class_['id'], False)
        users.extend([f"{user['name']} - {class_['name']}" for user in students_class])
    await api.logout()

    result = "\n".join(users)
    
    await message.message.delete()
    await message.message.answer_document(types.InputFile(StringIO(result), "students.txt"), caption=f"*🧑‍🎓Ученики({len(users)})*", parse_mode="markdown")
    await message.message.answer(f"✅Готово", reply_markup=keyboard_info)

#text="teachers"
async def teachers(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    subjects = await api.subjects()
    await api.logout()
    
    teachers = []
    
    for subject in subjects:
        for teacher in subject['teachers']:
            teacher = f"{teacher['name']} - {subject['name']}"
            if teacher not in teachers: teachers.append(teacher)
    
    result = "\n".join(teachers)
    
    await message.message.delete()
    await message.message.answer_document(types.InputFile(StringIO(result), "teachers.txt"), caption=f"*👨‍🏫Преподаватели({len(teachers)})*", parse_mode="markdown")
    await message.message.answer(f"✅Готово", reply_markup=keyboard_info)

#text="class_info"
async def select_class_info(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    classes = await api.classes()
    await api.logout()
    
    keyboard = await keyboard_classes(classes, "class_info", "info")
    
    await message.message.edit_text(f"📕Выберите класс", reply_markup=keyboard)
    
#text_contains="class_info|"
async def class_info(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    class_, students = await api.class_info(message.data.split("|")[2])
    await api.logout()
    
    result = f"*📓Тип класса*: {class_['classType']['name']}\n"
    result += f"*🧑‍🏫Классный руководитель*: {class_['chiefs'][0]['name']}\n"
    result += f"\n*🔢Состав класса({len(students)})*:"
    for i, student in enumerate(students):
        result += f"\n{(await number_to_emoji(i))}{student['name']}"
    await message.message.edit_text(result, reply_markup=keyboard_info, parse_mode="markdown")

def register(dp: Dispatcher):
    dp.register_message_handler(info, commands=['info'], state="*")
    dp.register_callback_query_handler(info_button, text="info", state="*")
    dp.register_callback_query_handler(info_student, text="info_student", state="*")
    dp.register_callback_query_handler(info_school, text="info_school", state="*")
    dp.register_callback_query_handler(info_school_full, text='info_school_full', state="*")
    dp.register_callback_query_handler(sessions, text="info_sessions", state="*")
    dp.register_callback_query_handler(info_users, text="info_users", state="*")
    dp.register_callback_query_handler(students, text="students", state="*")
    dp.register_callback_query_handler(teachers, text="teachers", state="*")
    dp.register_callback_query_handler(select_class_info, text="class_info", state="*")
    dp.register_callback_query_handler(class_info, text_contains="class_info|", state="*")