from aiogram import Dispatcher, types
from aiogram.dispatcher import FSMContext
from .utils.maria import Maria
from .netschool.netschool import NetSchool
from .utils.keyboard import keyboard_back, keyboard_schedule, keyboard_classes, keyboard_teachers
from .utils.states import Schedule
from .utils.other import number_to_emoji, diary_to_schedule, week_days
from datetime import datetime, timedelta
from devtools import debug

maria = Maria()

#commands=['schedule']
async def schedule(message: types.Message, state: FSMContext):
    await state.finish()
    await Schedule.date.set()
    await message.answer(f"📕Выберите дату или введите её в формате DD.MM(пример: 21.01)", reply_markup=keyboard_schedule)
    
#text="schedule"
async def schedule_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await Schedule.date.set()
    await message.message.edit_text(f"📕Выберите дату или введите её в формате DD.MM(пример: 21.01)", reply_markup=keyboard_schedule)

#text_contains="schedule|"
async def get_schedule_button(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    date = message.data.split("|")[-1]
    if date == "week": start = None
    else:
        start = datetime.now() + timedelta(days=int(date))
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    diary = await api.diary(start=start, end=start)
    await api.logout()
    
    result = await diary_to_schedule(diary, start)
    
    await message.message.edit_text(result, reply_markup=keyboard_schedule, parse_mode='markdown')
    
#state="Schedule:date"
async def get_schedule_date(message: types.Message, state: FSMContext):
    await Schedule.date.set()
    message_edit = await message.answer(f"🔄Загрузка...")
    date = message.text.split("-")
    if len(date) == 1:
        start = datetime.strptime(date[0], "%d.%m").replace(year=datetime.now().year)
        end = start 
    else:
        start = datetime.strptime(date[0], "%d.%m").replace(year=datetime.now().year)
        end = datetime.strptime(date[1], "%d.%m").replace(year=datetime.now().year)
    await state.finish()
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    diary = await api.diary(start=start, end=end)
    await api.logout()
    
    result = await diary_to_schedule(diary, start)
    
    await message_edit.edit_text(result, reply_markup=keyboard_schedule, parse_mode='markdown')
    
#text="class_schedule"
async def select_class_schedule(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    classes = await api.classes()
    await api.logout()
    
    keyboard = await keyboard_classes(classes, "schedule", "schedule")
    
    await message.message.edit_text(f"📕Выберите класс", reply_markup=keyboard)
    
#text_contains="class|schedule"
async def advanced_class_schedule(message: types.CallbackQuery, state: FSMContext):
    await Schedule.date.set()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    class_id = message.data.split("|")[-1]
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    schedule = await api.advanced_schedule(class_id=class_id)
        
    result = ""
    
    subjects_dict = await api.subjects()
    times_dict = await api.times()
    await api.logout()
    
    subjects = {}
    for subject in subjects_dict:
        subjects[int(subject['id'])] = [subject['name'], subject['teachers'][0]['name']]
    debug(subjects)
        
    times = {}
    for time in times_dict:
        times[int(time['id'])] = [":".join(time['startTime'].split('T')[1].split(":")[:-1]), ":".join(time['endTime'].split('T')[1].split(":")[:-1])]
        
    week = {}
    for lesson in schedule:
        day = week_days[datetime.strptime(lesson['day'], "%Y-%m-%dT%H:%M:%S").weekday()]
        if not week.get(day): week[day] = []
        week[day].append(f"{(await number_to_emoji(lesson['number']))}{subjects[lesson['subjectGroupId']][0]}({times[lesson['scheduleTimeId']][0]}-{times[lesson['scheduleTimeId']][1]}) у {subjects[lesson['subjectGroupId']][1]}")
    
    for day in week:
        result += f"\n\n*{day}*\n"
        for lesson in week[day]:
            result += f"{lesson}\n"
    
    await message.message.edit_text(result, reply_markup=keyboard_schedule, parse_mode='markdown')
    
#text="teacher_schedule"
async def select_teacher_schedule(message: types.CallbackQuery, state: FSMContext):
    await Schedule.date.set()
    await message.answer()
    await message.message.edit_text("🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    teachers = await api.teachers()
    await api.logout()
    
    keyboard = await keyboard_teachers(teachers, "schedule", "schedule")
    
    await message.message.edit_text(f"👨‍🏫Выберите учителя", reply_markup=keyboard)
    
#text_contains="teacher|schedule"
async def advanced_teacher_schedule(message: types.CallbackQuery, state: FSMContext):
    await Schedule.date.set()
    await message.answer()
    await message.message.edit_text("🔄Загрузка...")
    
    teacher_id = message.data.split("|")[-1]
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    schedule = await api.advanced_schedule(teacher_id=teacher_id)
        
    result = ""
    
    times_dict = await api.times()
    classes = await api.classes()
    subjects_dict = {}
    for class_ in classes:
        subjects = await api.subjects(class_id=class_['id'])
        for subject in subjects:
            subjects_dict[subject['id']] = [subject['name'], class_['name']]
    await api.logout()
        
    times = {}
    for time in times_dict:
        times[int(time['id'])] = [":".join(time['startTime'].split('T')[1].split(":")[:-1]), ":".join(time['endTime'].split('T')[1].split(":")[:-1])]
        
    week = {}
    for lesson in schedule:
        day = week_days[datetime.strptime(lesson['day'], "%Y-%m-%dT%H:%M:%S").weekday()]
        if not week.get(day): week[day] = []
        if not subjects_dict.get(lesson['subjectGroupId']): continue
        week[day].append(f"{(await number_to_emoji(lesson['number']))}{subjects_dict[lesson['subjectGroupId']][0]}({times[lesson['scheduleTimeId']][0]}-{times[lesson['scheduleTimeId']][1]}) - {subjects_dict[lesson['subjectGroupId']][1]}")

    for day in week:
        result += f"\n*{day}*\n"
        for lesson in week[day]:
            result += f"{lesson}\n"
    
    await message.message.edit_text(result, reply_markup=keyboard_schedule, parse_mode='markdown')
    
def register(dp: Dispatcher):
    dp.register_message_handler(schedule, commands=['schedule'], state="*")
    dp.register_callback_query_handler(schedule_button, text="schedule", state="*")
    dp.register_callback_query_handler(advanced_class_schedule, text_contains="class|schedule", state="*")
    dp.register_callback_query_handler(advanced_teacher_schedule, text_contains="teacher|schedule", state="*")
    dp.register_callback_query_handler(get_schedule_button, text_contains="schedule|", state="*")
    dp.register_message_handler(get_schedule_date, state=Schedule.date)
    dp.register_callback_query_handler(select_class_schedule, text="class_schedule", state="*")
    dp.register_callback_query_handler(select_teacher_schedule, text="teacher_schedule", state="*")