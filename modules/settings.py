from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from .utils.maria import Maria
from .utils.keyboard import keyboard_settings

maria = Maria()

#commands=['settings']
async def settings(message: types.Message, state: FSMContext):
    await state.finish()
    
    settings = await maria.get_settings(message.from_user.id)
    keyboard = await keyboard_settings(*settings)
    
    await message.answer(f"🔧Настройки", reply_markup=keyboard)
    
#text="settings"
async def settings_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    
    settings = await maria.get_settings(message.from_user.id)
    keyboard = await keyboard_settings(*settings)
    
    await message.message.edit_text(f"⚙️Настройки", reply_markup=keyboard)
    
#text_contains="settings|"
async def edit_settings(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    _, type_settings, now_value = message.data.split("|")
    
    value = 1 if not int(now_value) else 0
    
    if type_settings == "notification_mark":
        await maria.update_setting_mark(message.from_user.id, value)
    else:
        await maria.update_setting_auth(message.from_user.id, value)
    
    settings = await maria.get_settings(message.from_user.id)
    keyboard = await keyboard_settings(*settings)
    
    await message.message.edit_text(f"⚙️Настройки", reply_markup=keyboard)
    
def register(dp: Dispatcher):
    dp.register_message_handler(settings, commands=['settings'], state="*")
    dp.register_callback_query_handler(settings_button, text="settings", state="*")
    dp.register_callback_query_handler(edit_settings, text_contains="settings|", state="*")