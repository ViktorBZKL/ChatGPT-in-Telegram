import logging
from modules.handlers import start
from modules.roles import role_handler
from modules.chatgpt import reset, chat_gpt
from modules.dispatcher import dp
from aiogram.utils import executor
from modules.admin import send_advertise

logging.basicConfig(filename='errors/errors.log', level=logging.ERROR, format='%(asctime)s %(levelname)s %(lineno)d %(message)s')

dp.register_message_handler(start, commands=['start', 'help'])
dp.register_message_handler(send_advertise, commands=['admin'])

dp.register_message_handler(role_handler, commands=['role'])

dp.register_message_handler(reset, commands=['reset'])
dp.register_message_handler(chat_gpt, lambda message: message.text)

if __name__ == '__main__':
    try:
        executor.start_polling(dp)
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")