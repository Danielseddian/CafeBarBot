import logging

from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from typing import Union, List, Dict, Tuple

from core.messanger import respond, respond_with_photo
from database import sql_db
from localization import ru
from keyboards.admin_kb import back_kb
from keyboards.base_kb import make_inline_buttons


class LevelControl:
    """Level control for keyboards"""

    def __init__(self):
        self.up = self.__no_keyboard

    @staticmethod
    async def __no_keyboard(message: Message) -> None:
        """Sends message, if there is no keyboard or keyboard has been broken"""
        await respond(message, ru.MSG_NO_KEYBOARD, del_msg=False)

    @staticmethod
    async def __top_level(message: Message) -> None:
        """Sends message, if user is on the top of keyboard's level"""
        await respond(message, ru.MSG_TOP_LEVEL, del_msg=False)

    def add(self, function):
        """Setups a function as a top keyboards level"""
        self.up = function

    def top(self):
        """Setups keyboard's level as a top"""
        self.up = self.__top_level

    def nope(self):
        """Setups no keyboard status"""
        self.up = self.__no_keyboard


class FSMAdd(StatesGroup):
    """FSM State to add new product"""

    category = State()
    image = State()
    name = State()
    description = State()
    price = State()
    count = State()


class FSMDel(StatesGroup):
    """FSM State to delete a product"""

    category = State()


class FSMCng(StatesGroup):
    """FSM State to change a product"""

    category = State()


class FSMCart(StatesGroup):
    """FSM State to add a product in user's cart"""

    count = State()


class FSMFindPayment(StatesGroup):
    """FSM State to find payment"""

    payment = State()


def check_user_registration(tg_id) -> None:
    """
    Checks user's registration and registers him if he's not registered
    :param tg_id: User's telegram id
    :return: Registered user
    """
    if not sql_db.check_user(tg_id):
        logging.info(ru.INF_REGISTER_USER.format(tg_id))
        try:
            sql_db.add_user(tg_id)
        except Exception as exc:
            logging.error(exc)
        else:
            logging.info(ru.INF_USER_REGISTERED.format(tg_id))


async def check_category(message: Message) -> str:
    """
    Checks categories in config and return category's slug
    :param message: Aiogram message object
    :return: Category's slug
    """
    name = message.text
    category = ru.KITCHEN_CATEGORIES.get(name) or ru.BAR_CATEGORIES.get(name) or ru.HOOKAH_CATEGORIES.get(name)
    if not category:
        await message.reply(ru.ERR_NO_CATEGORY)
        return ""
    return category


async def check_menu(message: Message, category: str, state: FSMContext) -> List:
    """
    Checks positions in database and return queryset of objects
    :param message: Aiogram message object
    :param category: Category's slug
    :param state: Aiogram FSMContext
    :return: Queryset menu
    """
    if category:
        await state.finish()
        menu: List = sql_db.get_menu(category, count=-1)
        if menu:
            return menu
        await respond(message, ru.MSG_MENU_EMPTY, back_kb)
    return []


async def delete_position(name: str, message: Union[Message, CallbackQuery]) -> None:
    """
    Delete product's position from database
    :param name: Product's name
    :param message: Aiogram message object
    :return: Deleted position from product db
    """
    logging.info(ru.INF_POSITION_START_DEL.format(name))
    try:
        sql_db.del_product(name)
    except Exception as exc:
        logging.error(exc)
    if sql_db.check_product_name(name):
        await respond(message, text=ru.ERR_ADMIN_NOT_DELETED.format(name))
    else:
        logging.info(ru.MSG_ADMIN_DELETED.format(name))
        await respond(message, text=ru.MSG_ADMIN_DELETED.format(name))


async def change_or_create_position(data: Dict, message: Message, old_name: str = "") -> None:
    """
    Check and create or update product in database
    :param data: Product's data
    :param message: Aiogram message object
    :param old_name: Old product's name to remove duplicate
    :return: Created or updated product in database
    """
    name = data["name"]
    logging.info(ru.INF_POSITION_START_ADD.format(name))
    try:
        changed: int = sql_db.add_product(data)
    except Exception as exc:
        logging.error(exc)
        await respond(message, ru.ERR_ADMIN_CANT_ADD.format(name), del_msg=False)
    else:
        if old_name:
            await delete_position(old_name, message)
        if changed:
            await respond(message, ru.MSG_ADMIN_UPDATED.format(name), del_msg=False)
        else:
            await respond(message, ru.MSG_ADMIN_ADDED.format(name), del_msg=False)


async def show_menu(menu: List, message: Message, button: str, callback: str, admin: bool = False) -> None:
    """
    Shows menu and inline button
    :param menu: List of products data
    :param message: Aiogram message object
    :param button: Button's message
    :param callback: Query callback
    :param admin: If not admin shows count without ordered products
    :return: Shown menu with inline buttons
    """
    for dish in menu:
        name: str = dish[1]
        if not admin:
            text: str = ru.MSG_DISH.format(*dish[1:-1], dish[-1] - sql_db.get_ordered(name, message.from_user.id))
        else:
            text: str = " ".join((ru.MSG_DISH.format(*dish[1:]), ru.MSG_IN_ORDERS.format(sql_db.get_ordered(name, 0))))
        markup = make_inline_buttons((button.format(name),), (callback.format(name),))
        await respond_with_photo(message, dish[0], text, markup, del_msg=False)


async def show_orders(orders: List, message: Message, buttons: Tuple, callbacks: Tuple) -> float:
    """
    Shows user's orders
    :param orders: List of user orders
    :param message: Aiogram message object
    :param buttons: Tuple of buttons
    :param callbacks: Tuple of callback data
    :return: Shown user's orders and total price of orders
    """
    total: float = 0.0
    for order in orders:
        name: str = order[1]
        markup = make_inline_buttons(
            (buttons[0].format(name), buttons[1].format(name)), (callbacks[0].format(name), callbacks[1].format(name))
        )
        price: float = order[-1] * order[-2]
        total += price
        text: str = " ".join((ru.MSG_DISH.format(*order[1:]), ru.MSG_PRICE.format(price)))
        await respond_with_photo(message, order[0], text, markup, del_msg=False)
    return total


def make_report(in_order: bool = True) -> dict:
    """
    Make report dict: dish-data
    :return: Made report dict
    """
    payments: tuple = tuple(payment[0] for payment in sql_db.get_in_time_payments())
    orders: dict = dict()
    for order in sql_db.get_report(payments, in_order):
        if order[0] in orders:
            dish: dict = orders[order[0]]
            dish["paid_count"] += order[1]
            dish["total_price"] += order[1] * order[2]
            dish["order_count"] += order[3]
        else:
            orders[order[0]] = {"paid_count": order[1], "total_price": order[1] * order[2], "order_count": order[3]}
    return orders


async def get_payment_products(message, payment_id) -> bool:
    """
    Make list of payment's product's and theirs count in order
    :param message: Aiogram Message object
    :param payment_id: Payment id in database
    :return: Shown list of payment's products
    """
    products: list = sql_db.get_paid_products(payment_id)
    print(payment_id)
    if not products:
        return False
    length: int = 0
    responses: list = [[]]
    for product in products:
        product_msg: str = ru.MSG_ADMIN_PAID_PRODUCT.format(payment_id, product[0], product[1])
        length += len(product_msg) + 1
        if length > 500:
            responses.append([])
            length: int = len(product_msg) + 1
        responses[-1].append(product_msg)
    for response in responses:
        await respond(message, "\n".join(response), del_msg=False)
    return True


LEVEL = LevelControl()


if __name__ == '__main__':
    print(make_report())
