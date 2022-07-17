# -------------------------------------------------------------------------------------------------------------------- #
# Imports                                                                                                              #
# -------------------------------------------------------------------------------------------------------------------- #
import logging
from pathlib import Path

from dotenv import load_dotenv
from environ import Env

# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Time settings                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
START_SHIFT = 5, 0  # начало смены: часы, минуты через запятую, например: 5, 0 == 5:00
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# .env variables                                                                                                       #
# -------------------------------------------------------------------------------------------------------------------- #
load_dotenv()
env = Env()

TOKEN = env("TG_TOKEN")
ADMINS = tuple(map(int, env("ADMIN_IDS").split()))
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Payment params                                                                                                       #
# -------------------------------------------------------------------------------------------------------------------- #
TERMINAL_KEY = env("TERMINAL_KEY")
TERMINAL_PASSWORD = env("TERMINAL_PASSWORD")
INIT_PAYMENT_API = env("TINKOFF_INIT_API")
INIT_PAYMENT_RETRIES = 3, 5  # Количество попыток, перерыв между запросами (сек) - для получения платежной ссылки
STATE_PAYMENT_API = env("TINKOFF_STATE_API")
STATE_PAYMENT_RETRIES = 120  # Перерыв между запросами (сек) - для получения статуса платежа
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Directories and defaults                                                                                             #
# -------------------------------------------------------------------------------------------------------------------- #
BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_ROOT = BASE_DIR / "file_store"
MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
TEMP = BASE_DIR / "temp"
TEMP.mkdir(parents=True, exist_ok=True)
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Logging settings                                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
logging.basicConfig(
    filename=BASE_DIR / "bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
log = logging.getLogger("CafeBarBot")
# -------------------------------------------------------------------------------------------------------------------- #
