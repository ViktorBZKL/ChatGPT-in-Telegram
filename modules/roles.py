import os
import csv
import logging
from modules.transliterate import transliterate
from modules.dispatcher import bot, dp
from aiogram.dispatcher import FSMContext
from modules.user_messages import user_messages, roles
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, Message

class Roles(StatesGroup):
    category = State()
    role = State()

@dp.message_handler(commands=['role'])
async def role_handler(message: Message):
    try:
        user_id = message.chat.id
        markup = InlineKeyboardMarkup()
        markup.add(
            InlineKeyboardButton("Стандартный режим", callback_data='standard')
        )
                
        for category in os.listdir('templates'):    
            category_name = category.split('.')[0]
            markup.add(
                InlineKeyboardButton(category_name, callback_data=transliterate(category_name))
            )
            with open(f'templates/{category}', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                roles[category_name] = {}
                for row in reader:
                    role = row['act']
                    prompt = row['prompt']

                    roles[category_name][role] = prompt
                    
        await bot.send_message(user_id, "Выберите категорию:", reply_markup=markup)
        await Roles.category.set()
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")

@dp.callback_query_handler(lambda call: call.data not in ['based', 'advanced', 'premium'], state=Roles.category)
async def handle_callback(call: CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        if call.data == 'standard':
            user_messages[user_id] = []
            await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                        text="Вы выбрали стандартный режим.")
        else:
            for category in roles.keys():
                if call.data == transliterate(category):
                    markup = InlineKeyboardMarkup()

                    for role in roles[category].keys():
                        button = InlineKeyboardButton(text=role, callback_data=f'{transliterate(role)}')
                        markup.add(button)
                    markup.add(
                        InlineKeyboardButton(text='Назад', callback_data=f'back')
                    )
                    await state.update_data(selected_category=category)
                    await Roles.role.set()
                    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
                                                text="Выберите режим:", reply_markup=markup)
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")

                    
@dp.callback_query_handler(state=Roles.role)
async def handle_category(call: CallbackQuery, state: FSMContext):
    try:
        user_id = call.message.chat.id
        if call.data == 'back':
            markup = InlineKeyboardMarkup()
            markup.add(
                InlineKeyboardButton("Стандартный режим", callback_data='standard')
            )
                    
            for category in os.listdir('templates'):    
                category_name = category.split('.')[0]
                markup.add(
                    InlineKeyboardButton(category_name, callback_data=transliterate(category_name))
                )
            await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id, 
                                                text="Выберите категорию:", reply_markup=markup)
            await Roles.category.set()

        else:
            state_data = await state.get_data()
            category = state_data.get('selected_category')

            for role in roles[category].keys():
                if call.data == transliterate(role):
                    user_messages[user_id] = []
                    user_messages[user_id].append({"role": "system", "content": roles[category][role]})
                    await bot.edit_message_text(chat_id=user_id, message_id=call.message.message_id,
                                        text=f"Выбран режим: <b>{role}</b>.", parse_mode='HTML')
            await state.finish()
    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")
        await state.finish()