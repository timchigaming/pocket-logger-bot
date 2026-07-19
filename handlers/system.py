from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv('../.env')

from helpers.rights import is_admin, IsAdmin
from helpers.system import execute_internal, system_info_internal, halt_execute_internal
from keyboards.stop_executing_shells import get_executing_shells_keyboard

#------BOT-------
system_router = Router()

#------VARS------

#----------------#----------------#----------------
@system_router.message(Command("execute"), IsAdmin())
async def execute_shell(message: Message):
    cmd = message.text[8:].strip()
    if "sudo" in cmd or "rm -rf" in cmd: 
        await message.reply("Команды уровня суперпользователя пока что не поддерживаются.")
        return
    
    text = await execute_internal(cmd)
    await message.reply(text, parse_mode=ParseMode.HTML)

@system_router.message(Command("system_info"), IsAdmin())
async def get_system_info(message: Message):
    text = system_info_internal()
    await message.reply(text, parse_mode=ParseMode.HTML)

@system_router.message(Command("system_monitor"), IsAdmin())
async def get_system_monitor(message: Message):
    # psutil + fancy view + auto-update by... some kind of couroutine or idk
    pass

@system_router.message(Command("halt_execute"), IsAdmin())
async def halt_execute_shell(message: Message):
    reply_keyboard = get_executing_shells_keyboard()
    
    text = "Активных задач нет" 
    if reply_keyboard:
        text = "Какую из запущенных задач остановить?"
        
    await message.answer(text, reply_markup=reply_keyboard)

@system_router.callback_query(F.data.contains("killp"))
async def halt_execute_shell_callback(callback: CallbackQuery):
    pid = int(callback.data[6:])
    return_code = await halt_execute_internal(pid)
    text = f"Процесс с PID {pid} завершён. Код возврата: {return_code}"
    await callback.message.reply(text, parse_mode=ParseMode.HTML)

#----------------#----------------#----------------
