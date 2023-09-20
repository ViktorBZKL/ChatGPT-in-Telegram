import sqlite3
import openai
import logging
from modules.dispatcher import bot, dp
from modules.user_messages import user_messages
from aiogram.types import Message

@dp.message_handler(commands=['reset'])
async def reset(message: Message):
    try:
        user_id = message.chat.id
        user_messages[user_id] = []
        await message.reply("Контекст сброшен, выбран стандартный режим")
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")

@dp.message_handler(lambda message: message.text)
async def chat_gpt(message: Message):
    try:
        user_id = message.chat.id
        if user_id not in user_messages:
            user_messages[user_id] = []

        user_messages[user_id].append({"role": "user", "content": message.text})
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-3.5-turbo",
                messages=user_messages[user_id]
            )
            reply = response.choices[0].message.content

            connect = sqlite3.connect('users.db')
            cursor = connect.cursor()
            cursor.execute(f"SELECT tokens FROM login_id WHERE id = {user_id}")
            result = cursor.fetchone()
            totalTokens = response.usage["total_tokens"]
            if result:
                current_tokens = result[0]
                new_tokens = totalTokens + current_tokens
                cursor.execute(f"UPDATE login_id SET tokens = '{new_tokens}' WHERE id = {user_id}")
            else:
                cursor.execute(f"UPDATE login_id SET tokens = '{totalTokens}' WHERE id = {user_id}")
            connect.commit()

        except Exception as e:
            if "overloaded with other requests" in str(e):
                await bot.send_message(chat_id=user_id,
                                text="Бот перегружен. Попробуйте отправить свой запрос позже.")
            elif "maximum context length is 4097" in str(e):
                await bot.send_message(chat_id=user_id,
                                text="Превышена максимальная длина диалога. Был создан новый диалог.")
                reset(message)
            elif "please check your plan and billing details" or "The OpenAI account associated with this API key has been deactivated" in str(e):
                await bot.send_message(chat_id=message.chat.id, text="Бот временно не работает. Идут технические работы.")                
            else:
                await bot.send_message(chat_id=user_id,
                                text="Произошла непредвиденная ошибка в обработке вашего запроса. Пожалуйста, попробуйте еще раз или создайте новый диалог с помощью команды /reset.")
            logging.error(f"An error occurred: {repr(e)}")
            return

        await bot.send_chat_action(user_id, 'typing')
        await bot.send_message(chat_id=user_id, text=reply)
        user_messages[user_id].append({"role": "assistant", "content": reply})

    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")