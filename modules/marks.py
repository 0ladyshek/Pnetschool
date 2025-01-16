from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from .utils.keyboard import keyboard_marks
from .utils.maria import Maria
from .netschool.netschool import NetSchool
from .utils.other import diary_to_marks, diary_to_advanced_marks, too_long_result, diary_to_report

maria = Maria()

#commands=['marks']
async def marks(message: types.Message, state: FSMContext):
    await state.finish()
    message_edit = await message.answer(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    start, end = await api.start_term(), await api.end_term()
    diary = await api.diary(start=start, end=end)
    await api.logout()
    
    result = await diary_to_marks(diary)
    
    await message_edit.edit_text(result, reply_markup=keyboard_marks, parse_mode='markdown')
    
#text="marks"
async def marks_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка....")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    start, end = await api.start_term(), await api.end_term()
    diary = await api.diary(start=start, end=end)
    await api.logout()
    
    result = await diary_to_marks(diary)
    
    await message.message.edit_text(result, reply_markup=keyboard_marks, parse_mode='markdown')
    
#text="advanced_marks"
async def advanced_marks(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await state.finish()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    start, end = await api.start_term(), await api.end_term()
    diary = await api.diary(start=start, end=end)
    await api.logout()
    
    result = await diary_to_advanced_marks(diary)
    result = await too_long_result(result)
    
    await message.message.delete()
    for i in result:
        await message.message.answer(i, parse_mode='markdown')
    await message.message.answer(f"✅Готово", reply_markup=keyboard_marks)
    
#text="report_marks"
async def report_marks(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await state.finish()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    start, end = await api.start_term(), await api.end_term()
    diary = await api.diary(start=start, end=end)
    await api.logout()
    
    result = await diary_to_report(diary)
    result = await too_long_result(result)
    
    await message.message.delete()
    for i in result:
        await message.message.answer(i, parse_mode='markdown')
    await message.message.answer(f"✅Готово", reply_markup=keyboard_marks)
    
def register(dp: Dispatcher):
    dp.register_message_handler(marks, commands=['marks'], state="*")
    dp.register_callback_query_handler(marks_button, text="marks", state="*")
    dp.register_callback_query_handler(advanced_marks, text="advanced_marks", state="*")
    dp.register_callback_query_handler(report_marks, text="report_marks", state="*")