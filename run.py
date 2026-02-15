import asyncio
import logging
import os

from aiogram import types, Bot, Dispatcher
from dotenv import load_dotenv

from handlers import router
from database import create_table

# Загружаем .env
load_dotenv()

# Берем токен
TOKEN = os.getenv("TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

async def main():
    await create_table()
    dp.include_router(router)

    await bot.set_my_commands([
        types.BotCommand(command='/start', description='Начало'),
        types.BotCommand(command='/rules', description='Правила'),
        types.BotCommand(command='/my_info', description='Моя информация'),
        types.BotCommand(command='/top', description='Рейтинг')
    ])

    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit!')
