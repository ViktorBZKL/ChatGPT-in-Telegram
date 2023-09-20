import os
import openai
import logging
from dotenv import load_dotenv
from modules.handlers import start, info
from modules.roles import role_handler
from modules.images import paint
from modules.chatgpt import reset, chat_gpt
from modules.dispatcher import dp
from aiogram.utils import executor

logging.basicConfig(filename='errors/errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(lineno)d %(message)s')

load_dotenv()

openai.api_key = os.environ.get('OpenAI')

dp.register_message_handler(start, commands=['start', 'help'])
dp.register_message_handler(info, commands=['info'])

dp.register_message_handler(role_handler, commands=['role'])

dp.register_message_handler(paint, commands=['image'])
dp.register_message_handler(reset, commands=['reset'])
dp.register_message_handler(chat_gpt, lambda message: message.text)

if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")