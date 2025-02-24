import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, types
from dotenv import load_dotenv

from database.engine import create_db, drop_db, session_maker
from handlers.admin import admin_router
from handlers.user import user_canal_router
from keyboards.bot_cmds_list import bot_cmds
from middlewares.db import DataBaseSession
from middlewares.media import MediaMiddleware
from scheduler.scheduler import scheduler

load_dotenv()


TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')


logging.basicConfig(level=logging.INFO)


dp: Dispatcher = Dispatcher()
bot: Bot = Bot(token=TELEGRAM_TOKEN)
dp.include_router(admin_router)
dp.include_router(user_canal_router)


async def on_startup(bot):
    '''Запускает БД.'''

    run_param = True
    if run_param:
        await drop_db()

    await create_db()


async def on_shutdown(bot):
    scheduler.shutdown()
    print('Бот выключен.')


async def main():
    '''Запуск бота.'''
    dp.message.middleware(MediaMiddleware())
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    dp.update.middleware(DataBaseSession(session_pool=session_maker))

    await bot.delete_webhook(drop_pending_updates=True)

    await bot.set_my_commands(commands=bot_cmds,
                              scope=types.BotCommandScopeAllPrivateChats())

    while True:
        scheduler.start()
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
