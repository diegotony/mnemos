import os
from datetime import datetime, timedelta
import pytz
from dotenv import load_dotenv

load_dotenv()

# Lee la zona horaria desde .env (por defecto UTC si no se define)
TZ_NAME = os.getenv("TIMEZONE", "UTC")
LOCAL_TZ = pytz.timezone(TZ_NAME)


def now_local():
    """Devuelve la fecha/hora actual con zona horaria configurada"""
    return datetime.now(LOCAL_TZ)


def parse_date_param(date_str: str) -> tuple[datetime, datetime]:
    """
    Parsea el parámetro 'date' y retorna (start_datetime, end_datetime).

    Soporta:
    - 'today': inicio y fin del día actual
    - 'tomorrow': inicio y fin de mañana
    - 'YYYY-MM-DD': inicio y fin de esa fecha específica

    Raises:
        ValueError: Si el formato no es válido

    Returns:
        tuple[datetime, datetime]: (start_datetime, end_datetime) con timezone
    """
    date_lower = date_str.lower().strip()

    if date_lower == "today":
        # Día actual
        now = now_local()
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end

    elif date_lower == "tomorrow":
        # Mañana
        now = now_local()
        tomorrow = now + timedelta(days=1)
        start = tomorrow.replace(hour=0, minute=0, second=0, microsecond=0)
        end = tomorrow.replace(hour=23, minute=59, second=59, microsecond=999999)
        return start, end

    else:
        # Intentar parsear como YYYY-MM-DD
        try:
            # Parsear la fecha
            naive_date = datetime.strptime(date_str, "%Y-%m-%d")

            # Agregar timezone
            start = LOCAL_TZ.localize(
                naive_date.replace(hour=0, minute=0, second=0, microsecond=0)
            )
            end = LOCAL_TZ.localize(
                naive_date.replace(hour=23, minute=59, second=59, microsecond=999999)
            )

            return start, end
        except ValueError:
            raise ValueError(
                "Invalid date format. Use 'today', 'tomorrow', or 'YYYY-MM-DD'"
            )
