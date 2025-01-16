from datetime import datetime

start_time = datetime.now()

from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from modules import *
from modules.utils.maria import Maria
from config import api_token
import logging

logging.basicConfig(level=logging.INFO) 
bot = Bot(token=api_token) 
dp = Dispatcher(bot, storage=MemoryStorage())

for module in modules:
    logging.warning(f"Register module {module.__name__}")
    module.register(dp)

async def start_db(dp):
    await Maria().start_db()

logging.warning(f"Startup took {datetime.now() - start_time} seconds")
executor.start_polling(dp, skip_updates=True, allowed_updates=['message', 'chat_member', 'callback_query', 'inline_query'], on_startup=start_db)