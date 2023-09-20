import openai
import sqlite3
import logging
from modules.dispatcher import bot, dp
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message

class YourStateEnum(StatesGroup):
    prompt = State()

@dp.message_handler(commands=['image'])
async def paint(message: Message):
    user_id = message.chat.id
    await bot.send_message(chat_id=user_id, text="Введите текст для генерации изображения")
    await YourStateEnum.prompt.set()
        



@dp.message_handler(state=YourStateEnum.prompt)
async def generate_image(message: Message, state: FSMContext):
    try:
        prompt = message.text
        response = await openai.Image.acreate(
            prompt=prompt,
            n=1,
            size="1024x1024"
        )
        image_url = response['data'][0]['url']
    except Exception as e:
        if "rejected as a result of our safety system" in str(e):
            await bot.send_message(chat_id=message.chat.id, text="К сожалению, ваш запрос был отклонен нашей системой безопасности из-за содержания недопустимого текста.")
        elif "hard limit has been reached" in str(e):
            await bot.send_message(chat_id=message.chat.id, text="Бот временно не работает. Идут технические работы.")                
        else:
            await bot.send_message(chat_id=message.chat.id, text="Произошла непредвиденная ошибка в обработке вашего запроса. Пожалуйста, попробуйте еще раз.")                
        await state.finish()
        logging.error(f"An error occurred: {repr(e)}")
        return
    try:
        await bot.send_chat_action(message.chat.id, 'upload_photo')
        await bot.send_photo(chat_id=message.chat.id, photo=image_url)


        connect = sqlite3.connect('users.db')
        cursor = connect.cursor()
        cursor.execute(f"UPDATE login_id SET images = images+1 WHERE id = {message.chat.id}")
        connect.commit()
        cursor.close()
        connect.close()
        await state.finish()
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")
        await state.finish()