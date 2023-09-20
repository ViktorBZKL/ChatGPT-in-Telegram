import sqlite3
import logging
from aiogram import types
from modules.dispatcher import bot, dp
from modules.messages import startMessage

@dp.message_handler(commands=['start', 'help'])
async def start(message: types.Message):
    try:
        await bot.send_message(chat_id=message.chat.id, text=startMessage)
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS login_id(
            id INTEGER,
            username TEXT,
            tokens BIGINT DEFAULT 0,
            images BIGINT DEFAULT 0
        )""")

        connect.commit()

        user_id = message.chat.id
        username = message.chat.username
        cursor.execute(f"SELECT id FROM login_id WHERE id = {user_id}")
        data = cursor.fetchone()
        if data is None:
            user_data = [user_id, username]
            cursor.execute("INSERT INTO login_id VALUES(?, ?, ?, ?);", (*user_data, 0, 0))
            connect.commit()
        
        cursor.close()
        connect.close()
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")

@dp.message_handler(commands=['info'])
async def info(message: types.Message):
    try:
        user_id = message.chat.id
        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"SELECT tokens, images FROM login_id WHERE id = {user_id}")
        result = cursor.fetchone()
        if result:
            tokens, images = result
            await bot.send_message(chat_id=user_id, text=f"Количество использованных токенов: {tokens}\nКоличество созданных изображений: {images}")
        else:
            await bot.send_message(chat_id=user_id, text="Ваши данные не найдены в базе данных.")
        cursor.close()
        connect.close()
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")
