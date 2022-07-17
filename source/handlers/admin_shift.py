import openpyxl
from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text
from datetime import datetime as dt

from core.config import ADMINS, TEMP
from core.messanger import respond, respond_file
from database import sql_db
from handlers.admin_menu import check_admin
from handlers.base import LEVEL, FSMFindPayment, make_report, get_payment_products
from localization import ru
from keyboards.admin_kb import back_kb, shift_kb
from keyboards.base_kb import make_inline_buttons


async def get_shift_commands(message: Message) -> None:
    """
    Shows menu's updating keyboard
    :param message: Aiogram message object
    :return: Shown menu's updating keyboard
    """
    LEVEL.add(check_admin)
    if message.from_user.id in ADMINS:
        LEVEL.add(check_admin)
        await respond(message, ru.MSG_ADMIN_SHIFT, shift_kb)


async def get_report(message: Message) -> None:
    """
    Shows menu's updating keyboard
    :param message: Aiogram message object
    :return: Shown menu's updating keyboard
    """
    if message.from_user.id in ADMINS:
        orders: dict = make_report()
        length: int = 0
        responses: list = [[]]
        revenue: float = 0.0
        in_order: int = 0
        for order, data in orders.items():
            revenue += data["total_price"]
            in_order += data["order_count"]
            reported_dish: str = ru.MSG_ADMIN_REPORT.format(order, *data.values())
            length += len(reported_dish) + 1
            if length > 500:
                length: int = len(reported_dish) + 1
                responses.append([])
            responses[-1].append(reported_dish)
        for response in responses:
            await respond(message, "\n".join(response), del_msg=False)
        await respond(message, ru.MSG_ADMIN_REVENUE.format(revenue, in_order))


async def ask_payment_to_find(message: Message, state: FSMContext = None) -> None:
    """
    Ask payment id to find it
    :param message: Aiogram Message object
    :param state: Aiogram FSMContext object
    :return: Payment's id request
    """
    LEVEL.add(check_admin)
    if message.from_user.id in ADMINS:
        await FSMFindPayment.payment.set()
        await respond(message, ru.MSG_ADMIN_ASK_PAYMENT)


async def find_payment(message: Message, state: FSMContext) -> None:
    """
    Find paid products
    :param message: Aiogram Message object
    :param state: Aiogram FSMContext object
    :return: Paid products
    """
    if message.from_user.id in ADMINS:
        payment_id: str = message.text
        if not payment_id.isdigit():
            await message.reply(ru.ERR_NOT_NUM, reply_markup=back_kb)
            return
        await state.finish()
        payment_products: bool = await get_payment_products(message, payment_id)
        if not payment_products:
            await respond(message, ru.MSG_ADMIN_NO_PAYMENT, shift_kb)
        payment_status: str = ru.PAYMENT_STATUS.get(sql_db.get_payment_status(payment_id), ru.UNKNOWN_STATUS)
        await respond(message, ru.MSG_ADMIN_PAYMENT_STATUS.format(payment_status), del_msg=False)
    else:
        await state.finish()


async def show_payment_products(message: Message) -> None:
    """
    Shows payment's products
    :param message: Aiogram message object
    :return: Shown payment's products
    """
    payments: tuple = tuple(payment[0] for payment in sql_db.get_in_time_payments())
    for payment in payments:
        await get_payment_products(message, payment)
    if not payments:
        await respond(message, ru.MSG_NO_ORDERS)
    else:
        await message.delete()


async def empty_buttons(message: Message) -> None:
    await message.delete()


async def ask_close_shift(message: Message) -> None:
    """
    Asks to close shift
    :param message: Aiogram Message object
    :return: Asked confirmation to close shift
    """
    if message.from_user.id in ADMINS:
        markup = make_inline_buttons((ru.NLN_CONFIRM, ru.NLN_CANCEL), ("confirm_close_shift", "decline_close_shift"))
        await respond(message, ru.MSG_ADMIN_CLOSE_SHIFT, markup)


async def close_shift(query: CallbackQuery) -> None:
    """
    Create and send report and close shift
    :param query: Aiogram Callback query
    :return: Closed shift and sent report
    """
    if query.from_user.id in ADMINS:
        if query.data == "confirm_close_shift":
            wb = openpyxl.Workbook()
            wb_list = wb.active
            orders: dict = make_report(in_order=False)
            total_price: float = 0.0
            wb_list.append(ru.XLSX_TABLE_TITLES)
            for product, data in orders.items():
                if data["paid_count"] > 0:
                    wb_list.append((product, data["paid_count"], data["total_price"]))
                    total_price += data["total_price"]
            wb_list.append(("", ru.XLSX_TABLE_CONCLUSION.format(dt.now().strftime("%D")), total_price))
            file_name: str = f"{dt.now().strftime('%d-%m-%y %H.%M')}.xlsx"
            wb.save(TEMP / file_name)
            sql_db.close_orders()
            await respond_file(query, TEMP / file_name, del_msg=False)
            await respond(query, ru.MSG_ADMIN_SHIFT_CLOSED.format(file_name))
        else:
            await respond(query, ru.MSG_ADMIN_CANCELED)
    else:
        await query.message.delete()


def reg_admin_shift_handlers(dp: Dispatcher) -> None:
    """
    Register admin shift handlers in the dispatcher of the bot
    :param dp: Dispatcher of the bot
    :return: Registered admin shift handlers
    """
    dp.register_message_handler(get_shift_commands, Text(equals=ru.CMD_UPD_ORDERS, ignore_case=True))
    dp.register_message_handler(get_report, Text(equals=ru.CMD_ADMIN_REPORT, ignore_case=True))
    dp.register_message_handler(ask_payment_to_find, Text(equals=ru.CMD_ADMIN_FND_PAYMENT, ignore_case=True))
    dp.register_message_handler(find_payment, state=FSMFindPayment.payment)
    dp.register_message_handler(ask_close_shift, Text(equals=ru.CMD_ADMIN_CLS_SHIFT, ignore_case=True))
    dp.register_message_handler(show_payment_products, Text(equals=ru.CMD_SHOW_PAID, ignore_case=True))
    dp.register_message_handler(empty_buttons, Text(equals=[">", "<"]))
    dp.register_callback_query_handler(
        close_shift, lambda q: q.data and (q.data == "confirm_close_shift" or q.data == "decline_close_shift")
    )
