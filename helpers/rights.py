import os
from dotenv import load_dotenv
load_dotenv('../.env')

from aiogram.filters import BaseFilter
from aiogram.types import Message

#------VARS------
TG_ADMIN_ID: int = int(os.getenv("TG_ADMIN_ID"))
#----------------

def is_admin(user_id: int) -> bool:
    if user_id == TG_ADMIN_ID:
        return True
    return False

class IsAdmin(BaseFilter):
    def __init__(self, user_ids: int | list[int] = TG_ADMIN_ID):
        self.user_ids = user_ids
    
    async def __call__(self, message: Message) -> bool:
        admin_ids = self.user_ids
        user_id = message.from_user.id
        if isinstance(admin_ids, int):
            return message.from_user.id == admin_ids
        else:
            return message.from_user.id in admin_ids 

#----------------#----------------#----------------
