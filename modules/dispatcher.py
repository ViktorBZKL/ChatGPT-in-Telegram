import os
from aiogram import Bot
from dotenv import load_dotenv
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

load_dotenv()

token = os.environ.get('Bot')

bot = Bot(token=token)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
