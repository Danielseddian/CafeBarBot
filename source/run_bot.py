from aiogram.utils import executor
from asyncio import get_event_loop

from core.config import logging
from core.create import dp
from database import sql_db
from handlers.admin_menu import reg_admin_menu_handlers
from handlers.admin_shift import reg_admin_shift_handlers
from handlers.client import reg_division_handlers
from handlers.menu import reg_menu_handlers
from handlers.payment import check_payment_status
from localization import ru


async def on_startup(_):
    logging.info(ru.INF_BOT_CONNECTED)
    sql_db.sql_start()


reg_admin_menu_handlers(dp)
reg_admin_shift_handlers(dp)
reg_division_handlers(dp)
reg_menu_handlers(dp)


if __name__ == '__main__':
    logging.info(ru.INF_START_CONNECTION)
    try:
        loop = get_event_loop()
        loop.create_task(check_payment_status())
        executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
    except Exception as exc:
        logging.error(exc)
        raise exc
