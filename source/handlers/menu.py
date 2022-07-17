import logging

from aiogram import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from datetime import datetime as dt

from core.messanger import respond
from database import sql_db
from handlers.base import LEVEL, check_user_registration, FSMCart, FSMContext, show_menu, show_orders
from handlers.payment import create_payment_url
from handlers.client import kitchen, bar, hookah, start
from keyboards.admin_kb import cancel_kb
from keyboards.base_kb import make_inline_buttons, get_order_kb
from keyboards.client_kb import base_kb
from localization import ru


# -------------------------------------------------------------------------------------------------------------------- #
# Menu's functions                                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
async def get_menu(message: Message, menu: list, top_level) -> None:
    """
    Registers user if he's not registered and shows menu
    :param message: Aiogram message object
    :param menu: Menu queryset
    :param top_level: Top level keyboard's function
    :return: Registered user and shown menu
    """
    check_user_registration(message.from_user.id)
    if not menu:
        await respond(message, ru.MSG_MENU_EMPTY)
        return
    LEVEL.add(top_level)
    await show_menu(menu, message, ru.NLN_ADD_TO_CART, "order_add {}")
    await respond(message, ru.MSG_SHOWN_MENU, base_kb)


async def show_kitchen_menu(message: Message) -> None:
    """
    Show kitchen menu
    :param message: Aiogram message object
    :return: Kitchen menu
    """
    await get_menu(message, sql_db.get_menu(ru.KITCHEN_CATEGORIES[message.text]), kitchen)


async def show_bar_menu(message: Message) -> None:
    """
    Show bar menu
    :param message: Aiogram message object
    :return: Bar menu
    """
    await get_menu(message, sql_db.get_menu(ru.BAR_CATEGORIES[message.text]), bar)


async def show_hookah_menu(message: Message) -> None:
    """
    Show hookah menu
    :param message: Aiogram message object
    :return: Hookah menu
    """
    await get_menu(message, sql_db.get_menu(ru.HOOKAH_CATEGORIES[message.text]), hookah)


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# User cart's functions                                                                                                #
# -------------------------------------------------------------------------------------------------------------------- #
async def add_to_cart(query: CallbackQuery, state: FSMContext = None) -> None:
    """
    Adds dishes into client's shopping cart
    :param query: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Added new position into client's shopping cart
    """
    LEVEL.add(start)
    product: str = query.data.replace("order_add ", "")
    await FSMCart.count.set()
    async with state.proxy() as data:
        data["product"] = product
    count: int = sql_db.check_in_pre_order(product, query.from_user.id)
    if count > 0:
        await respond(query, ru.MSG_CART_EXISTS.format(product, count), cancel_kb, del_msg=False)
    else:
        await respond(query, ru.MSG_ADD_COUNT.format(product), cancel_kb, del_msg=False)


async def set_order_count(message: Message, state: FSMContext) -> None:
    """
    Sets up order's count and save order
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Added order into shopping cart
    """
    LEVEL.add(start)
    count: str = message.text
    if not count.isdigit():
        await message.reply(ru.ERR_NOT_NUM)
        return
    count: int = int(count)
    if count <= 0:
        await message.reply(ru.ERR_NEG_NUM)
        return
    async with state.proxy() as data:
        product: str = data["product"]
    await state.finish()
    exists: int = sql_db.get_product_count(product) - sql_db.get_ordered(product, message.from_user.id)
    if count > exists:
        await respond(message, ru.ERR_NOT_ENOUGH.format(exists, product, exists), del_msg=False)
        count: int = exists
    sql_db.add_product_into_cart(product, message.from_user.id, count)
    await respond(message, ru.MSG_ADDED.format(product, count), del_msg=False)
    await LEVEL.up(message)


async def show_user_order_cart(message: Message) -> None:
    """
    Shows user's order cart
    :param message: Aiogram message object
    :return: Shown user's order cart
    """
    LEVEL.add(start)
    orders: list = sql_db.get_orders(message.from_user.id)
    if orders:
        total_price: float = await show_orders(
            orders, message, (ru.NLN_CHANGE_ORDER, ru.NLN_DEL_ORDER), ("order_add {}", "order_del {}")
        )
        await respond(message, ru.MSG_TO_PAY.format(total_price), get_order_kb(total_price))
    else:
        await respond(message, ru.MSG_NO_ORDERS, get_order_kb(0))


async def show_user_payments(message: Message) -> None:
    """
    Shows user's paid orders
    :param message: Aiogram message object
    :return: Shown user's paid orders
    """
    orders: list = sql_db.get_user_payments(message.from_user.id)
    if orders:
        for order in orders:
            readable_time: str = dt.fromtimestamp(order[2]).strftime("%D %H:%M")
            payment_status: str = ru.PAYMENT_STATUS.get(order[3], ru.UNKNOWN_STATUS)
            await respond(
                message,
                ru.MSG_USER_PAYMENTS.format(order[0], order[1], readable_time, payment_status),
                del_msg=False,
            )
        await respond(message, ru.MSG_ORDER_NUM_INF)
    else:
        await respond(message, ru.MSG_NO_PAYMENTS)


async def ask_del_from_cart(query: CallbackQuery) -> None:
    """
    Asks confirmation to delete order from order's cart
    :param query: Aiogram CallbackQuery object
    :return: Shown confirmation buttons
    """
    LEVEL.add(show_user_order_cart)
    name: str = query.data.replace("order_del ", "")
    markup = make_inline_buttons(
        (ru.NLN_CONFIRM, ru.NLN_CANCEL),
        (f"conf_ord_del{name}", f"decl_ord_del{name}"),
    )
    await respond(query, ru.MSG_CONFIRM_DEL_ORDER.format(name), markup, del_msg=False)


async def del_from_cart(query: CallbackQuery) -> None:
    """
    Deletes or cancels deletion order from user's cart
    :param query: Aiogram CallbackQuery object
    :return: Deleted order from user's cart
    """
    name: str = query.data.replace("conf_ord_del", "")
    if query.data.startswith("conf_ord_del"):
        sql_db.update_in_cart_product_count(0, name, query.from_user.id)
        await respond(query, ru.MSG_ADMIN_DELETED.format(name))
    else:
        await respond(query, ru.MSG_ADMIN_CANCELED)
    await LEVEL.up(query)


async def ask_del_my_cart(message: Message) -> None:
    """
    Asks confirmation to delete all order from order's cart
    :param message: Aiogram Message object
    :return: Shown confirmation buttons
    """
    LEVEL.add(show_user_order_cart)
    markup = make_inline_buttons((ru.NLN_CONFIRM, ru.NLN_CANCEL), ("confirm_orders_del", "cancel_orders_del"))
    await respond(message, ru.MSG_CONFIRM_DEL_ORDERS, markup)


async def del_my_cart(query: CallbackQuery) -> None:
    """
    Deletes or cancels deletion all orders from user's cart
    :param query: Aiogram CallbackQuery object
    :return: Deleted order from user's cart
    """
    if query.data == "confirm_orders_del":
        LEVEL.add(start)
        sql_db.cancel_user_orders(query.from_user.id)
        await respond(query, ru.MSG_ORDERS_DELETED)
    else:
        await respond(query, ru.MSG_ADMIN_CANCELED)
    await LEVEL.up(query)


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Payment's functions                                                                                                  #
# -------------------------------------------------------------------------------------------------------------------- #
async def ask_pay_orders(message: Message) -> None:
    """
    Asks confirmation to delete all order from order's cart
    :param message: Aiogram Message object
    :return: Shown confirmation buttons
    """
    LEVEL.add(show_user_order_cart)
    markup = make_inline_buttons((ru.NLN_CONFIRM, ru.NLN_CANCEL), ("confirm_orders_pay", "cancel_orders_pay"))
    await respond(message, ru.MSG_CONFIRM_PAY_ORDERS, markup)


async def ask_payment_url(query: CallbackQuery) -> None:
    """
    Requests payment's url and sends it to user
    :param query: Aiogram CallbackQuery object
    :return: Shown inline button with a link to pay
    """
    if query.data == "confirm_orders_pay":
        user_id: int = query.from_user.id
        orders: list = sql_db.get_orders_to_pay(user_id)
        if not orders:
            await respond(query, ru.MSG_NO_ORDERS)
            return
        total_price: float = sum(order[1] * order[2] for order in orders)
        payment_id: int = sql_db.create_payment(user_id, total_price)
        logging.info(ru.INF_START_DECLARATION)
        try:
            for order in orders:
                sql_db.make_payment_list(payment_id, *order)
                sql_db.sum_product_count(-1 * order[2], order[0])
            sql_db.cancel_user_orders(user_id)
        except Exception as exc:
            logging.error(exc)
            await respond(query, ru.MSG_PAY_CANCELED)
        else:
            logging.info(ru.MSG_ADMIN_PAYMENT_LIST_CREATED)
            payment_url: str = await create_payment_url(total_price, payment_id)
            markup = make_inline_buttons((ru.NLN_TO_PAY.format(total_price),), (payment_url,))
            await respond(query, ru.MSG_PAYMENT_LINK, markup)
    else:
        await respond(query, ru.MSG_PAY_CANCELED)


# -------------------------------------------------------------------------------------------------------------------- #


def reg_menu_handlers(dp: Dispatcher) -> None:
    """
    Register Caffe division's handlers in the dispatcher of the bot
    :param dp: Dispatcher of the bot
    :return: Registered handlers
    """
    for command in ru.KITCHEN_CATEGORIES.keys():
        dp.register_message_handler(show_kitchen_menu, Text(equals=command, ignore_case=True))
    for command in ru.BAR_CATEGORIES.keys():
        dp.register_message_handler(show_bar_menu, Text(equals=command, ignore_case=True))
    for command in ru.HOOKAH_CATEGORIES.keys():
        dp.register_message_handler(show_hookah_menu, Text(equals=command, ignore_case=True))
    dp.register_callback_query_handler(add_to_cart, lambda q: q.data and q.data.startswith("order_add "), state=None)
    dp.register_message_handler(set_order_count, state=FSMCart.count)
    dp.register_message_handler(show_user_order_cart, Text(equals=ru.CMD_MY_CART))
    dp.register_callback_query_handler(ask_del_from_cart, lambda q: q.data and q.data.startswith("order_del "))
    dp.register_callback_query_handler(
        del_from_cart, lambda q: q.data and (q.data.startswith("conf_ord_del") or q.data.startswith("decl_ord_del"))
    )
    dp.register_message_handler(ask_del_my_cart, Text(equals=ru.CMD_DEL_ORDERS))
    dp.register_callback_query_handler(
        del_my_cart, lambda q: q.data and (q.data == "confirm_orders_del" or q.data == "cancel_orders_del")
    )
    dp.register_message_handler(ask_pay_orders, Text(startswith=ru.CMD_ORDER[0]))
    dp.register_callback_query_handler(
        ask_payment_url, lambda q: q.data and (q.data == "confirm_orders_pay" or q.data == "cancel_orders_pay")
    )
    dp.register_message_handler(show_user_payments, Text(equals=ru.CMD_SHOW_MY_PAYMENTS))
