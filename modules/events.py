from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from datetime import datetime, timedelta
from pandas import date_range as dr
from .utils.maria import Maria
from .netschool.netschool import NetSchool
from .utils.keyboard import keyboard_back, keyboard_events, keyboard_birthdays
from .utils.other import birthday_to_year, month_emoji, too_long_result, clean_ads
import re
import html2markdown
import random

maria = Maria()

#commands=['events']
async def events(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(f"📆Выберите пункт меню", reply_markup=keyboard_events)
    
#text="events"
async def events_button(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"📆Выберите пункт меню", reply_markup=keyboard_events)
    
#text="birthday"
async def birthdays(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"📆Выберите месяц", reply_markup=keyboard_birthdays)
    
#text="birthdays|year"
async def get_birthdays_year(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()

    result = ""
    for month in range(1, 13):
        if month in [1, 2, 12]: emoji = random.choice(month_emoji['winter'])
        elif month in [3, 4, 5]: emoji = random.choice(month_emoji['spring'])
        elif month in [6, 7, 8]: emoji = random.choice(month_emoji['summer'])
        else: emoji = random.choice(month_emoji['autumn'])
        result += f"\n*{emoji}{datetime.now().replace(month=month).strftime('%B')}*:\n"
        birthdays = await api.birthdays(month)
        for birthday in birthdays:
            result += f"*{birthday['fio']}* - {datetime.strptime(birthday['birthdate'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}{(await birthday_to_year(birthday['birthdate']))}\n"
    await api.logout()

    result = await too_long_result(result)
    
    await message.message.delete()
    for i in result:
        await message.message.answer(i, parse_mode='markdown')
    await message.message.answer(f"✅Готово", reply_markup=keyboard_birthdays)
    
#text_contains="birthdays|"
async def get_birthdays_month(message: types.CallbackQuery, state: FSMContext):
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    month = (datetime.now() + timedelta(days=31 * int(message.data.split("|")[1]))).strftime("%m")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    birthdays_list = await api.birthdays(month)
    await api.logout()
    
    result = "🎂Дни рождения\n"
    for birthday in birthdays_list:
        result += f"*{birthday['fio']}* - {datetime.strptime(birthday['birthdate'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}{(await birthday_to_year(birthday['birthdate']))}\n"
    
    await message.message.edit_text(result, reply_markup=keyboard_birthdays, parse_mode='markdown')
    
#text="holidays"
async def holidays(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    year = (await api.years())[0]['name'].split("/")
    year_start = datetime.now().replace(month=1, day=1, year=int(year[0]))
    year_end = datetime.now().replace(month=11, day=1, year=int(year[1]))
    date_range = dr(start=year_start, end=year_end, freq='MS')
    
    holidays = []
    vacations = []
    
    for date in date_range:
        events = await api.holidays(month=date.month, year=date.year)
        for vacation in events['vacations']:
            name = f"🔥{vacation['name']}: {datetime.strptime(vacation['startTime'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}-{datetime.strptime(vacation['endTime'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}"
            if name in vacations: continue
            vacations.append(name)
        for holiday in events['holidays']:
            name = f"🎉{holiday['name']}: {datetime.strptime(holiday['startTime'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}-{datetime.strptime(holiday['endTime'], '%Y-%m-%dT00:00:00').strftime('%d.%m.%Y')}"
            if name in holidays: continue
            holidays.append(name)
    await api.logout()
    
    result = f"*🎉Праздники*\n" + '\n'.join(holidays) + "\n\n*😴Каникулы*\n" + '\n'.join(vacations)
    
    await message.message.edit_text(result, parse_mode='markdown', reply_markup=keyboard_events)
    
#text="ads"
async def ads(message: types.CallbackQuery, state: FSMContext):
    await state.finish()
    await message.answer()
    await message.message.edit_text(f"🔄Загрузка...")
    
    account = await maria.get_account_user(message.from_user.id)
    api = NetSchool(*account)
    await api.login()
    annoucements = await api.annouchements()
    await api.logout()
    
    if not annoucements: 
        return await message.message.edit_text(f"🫥Объявлений нет", reply_markup=keyboard_events)
    result = ""
    for annoucement in annoucements:
        result += f"{annoucement['author']['nickName']}\n{annoucement['postDate'].replace('T', '')}\n{annoucement['name']}\n{annoucement['description']}\n\n"
    result = html2markdown.convert(result)
    result = re.sub(clean_ads, '', result)
    
    await message.message.edit_text(result, parse_mode='markdown', reply_markup=keyboard_events)
    
def register(dp: Dispatcher):
    dp.register_message_handler(events, commands=['events'], state='*')
    dp.register_callback_query_handler(events_button, text="events", state='*')
    dp.register_callback_query_handler(birthdays, text="birthday", state='*')
    dp.register_callback_query_handler(get_birthdays_year, text="birthdays|year", state='*')
    dp.register_callback_query_handler(get_birthdays_month, text_contains="birthdays|", state='*')
    dp.register_callback_query_handler(holidays, text="holidays", state='*')
    dp.register_callback_query_handler(ads, text="ads", state='*')