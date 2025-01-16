from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from .utils.maria import Maria
from .utils.keyboard import keyboard_accounts, keyboard_menu
from .netschool.netschool import NetSchool

maria = Maria()

#commands=['start', 'menu']
async def menu(message: types.Message, state: FSMContext):
    await state.finish()
    account_id = await maria.user_exists(message.from_user.id)
    if account_id:
        return await message.answer(f"🎛️Добро пожаловать в главное меню. Выберите функцию", reply_markup=keyboard_menu)
    accounts = await maria.accounts_username_user(message.from_user.id)
    keyboard = await keyboard_accounts(accounts)
    await message.answer(f"🎛️Добро пожаловать. Выберите аккаунт из списка или добавьте новый", reply_markup=keyboard)
    
#text="menu"
async def menu_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    account_id = await maria.user_exists(message.from_user.id)
    if account_id:
        return await message.message.edit_text(f"🎛️Добро пожаловать в главное меню. Выберите функцию", reply_markup=keyboard_menu)
    accounts = await maria.accounts_username_user(message.from_user.id)
    keyboard = await keyboard_accounts(accounts)
    await message.message.edit_text(f"🎛️Добро пожаловать. Выберите аккаунт из списка или добавьте новый", reply_markup=keyboard)
    
#text_contains="account|"
async def select_account(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    account_id = message.data.split("|")[1]
    await maria.select_account(message.from_user.id, account_id)
    await message.message.edit_text(f"🎛️Добро пожаловать в главное меню. Выберите функцию", reply_markup=keyboard_menu)

#text="exit"
async def exit(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await maria.select_account(message.from_user.id)
    accounts = await maria.accounts_username_user(message.from_user.id)
    keyboard = await keyboard_accounts(accounts)
    await message.message.edit_text(f"🎛️Добро пожаловать в главное меню. Выберите аккаунт из списка или добавьте новый", reply_markup=keyboard)
    
def register(dp: Dispatcher):
    dp.register_message_handler(menu, commands=['start', 'menu'], state="*")
    dp.register_callback_query_handler(menu_button, text="menu", state="*")
    dp.register_callback_query_handler(select_account, text_contains="account|", state="*")
    dp.register_callback_query_handler(exit, text="exit", state="*")