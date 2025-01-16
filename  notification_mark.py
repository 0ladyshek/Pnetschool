from aiogram import Bot
from config import api_token
from modules.utils.maria import Maria
from modules.netschool.netschool import NetSchool
from datetime import datetime
import asyncio

maria = Maria()
bot = Bot(api_token)
loop = asyncio.get_event_loop()

async def notification_mark():
    users = await maria.get_users_notification_mark()
    for user in users:
        account = await maria.get_account_user(user[0])
        marks = await maria.get_user_marks(user[0])
        marks = [mark[0] for mark in marks]
        api = NetSchool(*account)
        await api.login()
        start, end = await api.start_term(), await api.end_term()
        diary = await api.diary(start=start, end=end)
        for day in diary['weekDays']:
            for lesson in day['lessons']:
                for assign in lesson['assignments']:
                    if assign.get('mark', {}).get('mark') and assign['mark']['mark'] and assign['mark']['id'] not in marks:
                        await bot.send_message(user[0], f"➕({datetime.strptime(assign['dueDate'], '%Y-%m-%dT%H:%M:%S').strftime('%d.%m')})Новая оценка {assign['mark']['mark']}{('(' + str(assign['weight']) + ')') if assign.get('weight') else ''} по {lesson['subjectName']} за {assign['assignmentName']}")
                        await maria.add_user_mark(user[0], assign['mark']['id'])
        await api.logout()

asyncio.run(notification_mark())