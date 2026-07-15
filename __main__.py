import asyncio, os, logging, time, datetime, subprocess, re, html
from dotenv import load_dotenv
load_dotenv()
from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import CommandStart, Command
from aiogram.enums import ParseMode


#----------------
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()
#----------------
TG_ADMIN_ID: int = int(os.getenv("TG_ADMIN_ID"))
OS_NAME = os.name

#----------------#----------------#----------------
@dp.message(CommandStart())
async def start(message: Message):
    answer = None
    if check_rights(message.from_user.id):
        answer = "Acess Granted."
    else:
        answer = "Я тебя не знаю, доступ не публичный, уходи.\n Приходи потом, через долгое время, может что-то поменяется."

    if answer:
        await message.reply(answer)

@dp.message(Command("ping"))
async def ping(message: Message):
    if (not check_rights(message.from_user.id)): return

    now = datetime.datetime.now(datetime.timezone.utc)

    ping_tg_ms = (now - message.date).total_seconds() * 1000
    text = f"Понг! Твой уровень IQ сегодня: {ping_tg_ms:.0f}\n А вот что насчёт сервера... "
    # Сделать пинг самого сервера ПОТОМ
    text += f"Он *живой*. {ping_tg_ms:.0f}"
    await message.answer(text, parse_mode=ParseMode.MARKDOWN)

@dp.message(Command("system"))
async def execute_shell(message: Message):
    if not check_rights(message.from_user.id): return

    cmd = message.text[8:].strip()
    if "sudo" in cmd or "rm -rf" in cmd: 
        await message.reply("Команды уровня суперпользователя пока что не поддерживаются.")
        return
    
    text = execute_internal(cmd)
    await message.reply(text, parse_mode=ParseMode.HTML)

@dp.shutdown()
async def on_shutdown(dispatcher: Dispatcher, bot: Bot):
    await bot.session.close()
    print("Stopped.")


#----------------#----------------#----------------
def check_rights(user_id: int) -> bool:
    if user_id == TG_ADMIN_ID:
        return True
    return False

def execute_internal(cmd: str):
    if not cmd: logging.error(f"execute_internal() called with an invalid set of arguments: {cmd}")

    then = time.time()
    proc_result = subprocess.run(cmd, 
                                shell=True, 
                                capture_output=True, 
                                encoding="cp866" if OS_NAME=="nt" else "utf-8", 
                                text=True)
    now = time.time()
    dt = f"{((now - then)):.0f}"
    
    safe_cmd = html.escape(cmd)
    safe_stdout = html.escape(proc_result.stdout)
    safe_stderr = html.escape(proc_result.stderr)

    text = f"""\
Запрос <code class="language-sh">{safe_cmd}</code> был обработан за <code>{dt}</code> секунд,
STDOUT:
<pre><code class="language-sh">{safe_stdout}</code></pre>
STDERR:
<pre><code class="language-sh"> {safe_stderr} </code></pre>
Return code <code>{proc_result.returncode}</code>.
"""
    return text

#----------------#----------------#----------------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    print("Initialized, working...")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Halted, stopping...")