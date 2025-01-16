from aiogram import Bot
from config import api_token
from modules.utils.maria import Maria
from modules.netschool.netschool import NetSchool
from datetime import datetime
import asyncio

maria = Maria()
bot = Bot(api_token)
loop = asyncio.get_event_loop()

async def notification_auth():
    now = datetime.now()
    users = await maria.get_users_notification_auth()
    for user in users:
        account = await maria.get_account_user(user[0])
        api = NetSchool(*account)
        await api.login()
        state = await api.state()
        await api.logout()
        for notification in state['notifications']:
            if notification['type'] == "security-warning":
                for worker in notification['data']['coWorkers']:
                    date = datetime.strptime(worker['loginTimeInto'].split(".")[0], "%Y-%m-%dT%H:%M:%S")
                    if (now - date).total_seconds() > 600: continue
                    await bot.send_message(user[0], f"⚠️{date.strftime('%H:%M')} была авторизация с {worker['ipAddress']}")

asyncio.run(notification_auth())