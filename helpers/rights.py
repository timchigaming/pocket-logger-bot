import os
from dotenv import load_dotenv
load_dotenv()

TG_ADMIN_ID: int = int(os.getenv("TG_ADMIN_ID"))

def check_rights(user_id: int) -> bool:
    if user_id == TG_ADMIN_ID:
        return True
    return False