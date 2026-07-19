from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpers.system import executing_shells

def get_executing_shells_keyboard():
    if not executing_shells: return None

    buttons = [
        [InlineKeyboardButton(text=cmd[:24], callback_data=f"killp {pid}")] 
        for cmd, pid, _ in executing_shells
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons, resize_keyboard=True)