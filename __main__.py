import asyncio, os, logging, time, datetime, subprocess, re, html
from dotenv import load_dotenv
load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode
from helpers.rights import is_admin, IsAdmin, TG_ADMIN_ID

from handlers.system import system_router

#------BOT-------
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
#------VARS------

#----------------#----------------#----------------
@dp.message(CommandStart())
async def start(message: Message):
    answer = None
    if is_admin(message.from_user.id):
        answer = "Acess Granted."
    else:
        answer = "Я тебя не знаю, доступ не публичный, уходи.\n Приходи потом, через долгое время, может что-то поменяется."

    if answer:
        await message.reply(answer)

@dp.message(Command("ping"), IsAdmin(TG_ADMIN_ID))
async def ping(message: Message):
    now = datetime.datetime.now(datetime.timezone.utc)

    ping_tg_ms = (now - message.date).total_seconds() * 1000
    text = f"Понг! Твой уровень IQ сегодня: {ping_tg_ms:.0f}\n А вот что насчёт сервера... "
    # Сделать пинг самого сервера ПОТОМ
    text += f"Он *живой*. {ping_tg_ms:.0f}"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.shutdown()
async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.session.close()
    print("Stopped.")


#----------------#----------------#----------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_router(system_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initialized, working...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Halted, stopping...")