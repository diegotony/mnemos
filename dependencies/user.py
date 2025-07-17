import os
from fastapi import Depends, HTTPException

DEFAULT_USER_ID = int(os.getenv("DEFAULT_USER_ID", 1))

def get_current_user_id() -> int:
    # En el futuro, reemplazás esto por lógica JWT
    if not DEFAULT_USER_ID:
        raise HTTPException(status_code=401, detail="No default user configured")
    return DEFAULT_USER_ID
