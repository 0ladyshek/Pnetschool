from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from .utils.maria import Maria
from .netschool.netschool import NetSchool
from .utils.keyboard import keyboard_back, keyboard_homework
from .utils.states import Homework
from .utils.other import diary_to_homework

maria = Maria()

#commands=['homework']
async def homework(message: types.Message, state: FSMContext):
    await Homework.date.set()
    await message.answer(f"📖Выберите дату или введите её в формате DD.MM(пример: 21.01)", reply_markup=keyboard_homework)
    
#text="homework"
async def homework_button(message: types.CallbackQuery ,state: FSMContext):
    await state.finish()
    await message.answer()
    await Homework.date.set()
    await message.message.edit_text(f"📖Выберите дату или введите её в формате DD.MM(пример: 21.01)", reply_markup=keyboard_homework)
    
#text_contains="homework|"
async def get_homework_button(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    date = message.data.split("|")[1]
    if date == "week":
        start = None
    else:
        start = datetime.now() + timedelta(days=int(date))
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    diary = await api.diary(start=start, end=start)
    await api.logout()
    
    result = await diary_to_homework(diary)
    
    await message.message.edit_text(result, reply_markup=keyboard_homework, parse_mode='markdown', disable_web_page_preview=True)
    
#state="Homework:date"
async def get_homework_date(message: types.Message, state: FSMContext):
    await Homework.date.set()
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
    
    result = await diary_to_homework(diary, start)
    
    await message_edit.edit_text(result, reply_markup=keyboard_homework, parse_mode='markdown', disable_web_page_preview=True)
    
def register(dp: Dispatcher):
    dp.register_message_handler(homework, commands=['homework'], state="*")
    dp.register_callback_query_handler(homework_button, text="homework", state="*")
    dp.register_callback_query_handler(get_homework_button, text_contains="homework|", state="*")
    dp.register_message_handler(get_homework_date, state=Homework.date)