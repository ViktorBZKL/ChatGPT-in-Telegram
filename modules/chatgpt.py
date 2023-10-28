import g4f
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
        
        providers = [
            g4f.Provider.Bing,
            # g4f.Provider.GeekGpt,
            g4f.Provider.Liaobots,
            g4f.Provider.Phind,
            # g4f.Provider.Raycast,
            # g4f.Provider.Aivvm,
            # g4f.Provider.GptChatly,
            # g4f.Provider.Lockchat,
            # g4f.Provider.Myshell,
            g4f.Provider.AItianhu,
            g4f.Provider.AItianhuSpace,
            g4f.Provider.AiAsk,
            g4f.Provider.Aichat,
            g4f.Provider.ChatBase,
            g4f.Provider.ChatgptAi,
            g4f.Provider.ChatgptFree,
            g4f.Provider.ChatgptX,
            g4f.Provider.FreeGpt,
            g4f.Provider.GPTalk,	
            g4f.Provider.GptForLove,
            g4f.Provider.GptGo,
            g4f.Provider.Llama2,
            g4f.Provider.NoowAi,
            g4f.Provider.OpenaiChat,
            g4f.Provider.You,
            # g4f.Provider.Yqcloud,
        ]

        user_messages[user_id].append({"role": "user", "content": message.text})
        response = None
        # for provider in providers:
        #     try:
        #         response = await g4f.ChatCompletion.create_async(
        #             model=g4f.models.default,
        #             messages=user_messages[user_id],
        #             provider=provider
        #         )
        #         reply = response
        #         break
        #     except Exception as e:
        #         await bot.send_message(chat_id=user_id, text=f"An error occurred: {repr(e)}")
        #         logging.error(f"An error occurred: {repr(e)}")
        #         return

        try:
            response = await g4f.ChatCompletion.create_async(
                model=g4f.models.default,
                messages=user_messages[user_id],
                provider=g4f.Provider.GPTalk
            )
            reply = response
        except Exception as e:
            await bot.send_message(chat_id=user_id, text=f"Ошибка. Попробуйте позже")
            logging.error(f"An error occurred: {repr(e)}")
            return

        await bot.send_chat_action(user_id, 'typing')
        await bot.send_message(chat_id=user_id, text=reply)
        user_messages[user_id].append({"role": "assistant", "content": reply})

    except Exception as e:
        logging.error(f"An error occurred: {repr(e)}")