from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import logging, html, os, time, subprocess
load_dotenv('../.env')
from helpers.rights import is_admin, IsAdmin

system_router = Router()
#------VARS------
OS_NAME = os.name

#----------------
@system_router.message(Command("system"))
async def execute_shell(message: Message):

    cmd = message.text[8:].strip()
    if "sudo" in cmd or "rm -rf" in cmd: 
        await message.reply("Команды уровня суперпользователя пока что не поддерживаются.")
        return
    
    text = execute_internal(cmd)
    await message.reply(text, parse_mode=ParseMode.HTML)


#----------------#----------------#----------------
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
