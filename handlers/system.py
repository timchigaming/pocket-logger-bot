from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from dotenv import load_dotenv

load_dotenv('../.env')

from helpers.rights import is_admin, IsAdmin
from helpers.system import execute_internal

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
    
    text = execute_internal(cmd)
    await message.reply(text, parse_mode=ParseMode.HTML)

@system_router.message(Command("system_info"), IsAdmin())
async def get_system_info(message: Message):
    # psutil, platform
    pass

@system_router.message(Command("system_monitor"), IsAdmin()):
async def get_system_load(message: Message):
    # psutil + fancy view + auto-update by... some kind of couroutine or idk
    pass

#----------------#----------------#----------------
