import os
from datetime import datetime
import pytz
from dotenv import load_dotenv

load_dotenv()

# Lee la zona horaria desde .env (por defecto UTC si no se define)
TZ_NAME = os.getenv("TIMEZONE", "UTC")
LOCAL_TZ = pytz.timezone(TZ_NAME)

def now_local():
    """Devuelve la fecha/hora actual con zona horaria configurada"""
    return datetime.now(LOCAL_TZ)