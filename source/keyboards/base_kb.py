from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from typing import Tuple, Union

from localization import ru


def append_kitchen_kb(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """
    Appends kitchen buttons to a keyboard
    :param keyboard: ReplyKeyboardMarkup object
    :return: Keyboard with appended buttons
    """
    keyboard.row(*(command for command in ru.KITCHEN_CATEGORIES.keys()))
    return keyboard


def append_bar_kb(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """
    Appends bar buttons to a keyboard
    :param keyboard: ReplyKeyboardMarkup object
    :return: Keyboard with appended buttons
    """
    keyboard.row(*(command for command in ru.BAR_CATEGORIES.keys()))
    return keyboard


def append_hookah_kb(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """
    Appends hookah buttons to a keyboard
    :param keyboard: ReplyKeyboardMarkup object
    :return: Keyboard with appended buttons
    """
    keyboard.row(*(command for command in ru.HOOKAH_CATEGORIES.keys()))
    return keyboard


def append_base_kb(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """
    Appends base buttons to a keyboard
    :param keyboard: ReplyKeyboardMarkup object
    :return: Keyboard with appended buttons
    """
    keyboard.row(KeyboardButton(ru.CMD_BACK), KeyboardButton(ru.CMD_HIDE_KB), KeyboardButton(ru.CMD_MY_CART))
    return keyboard


def append_categories_kb(keyboard: ReplyKeyboardMarkup) -> ReplyKeyboardMarkup:
    """
    Appends category's buttons to a keyboard
    :param keyboard: ReplyKeyboardMarkup object
    :return: Keyboard with appended buttons
    """
    append_kitchen_kb(keyboard)
    append_bar_kb(keyboard)
    append_hookah_kb(keyboard)
    return keyboard


def make_inline_buttons(buttons: tuple, callbacks: tuple) -> InlineKeyboardMarkup:
    """
    Create inline buttons
    :param buttons: Callbacks to confirm operation
    :param callbacks: Callbacks to decline operation
    :return: Created inline buttons
    """
    markup = InlineKeyboardMarkup()
    for index in range(len(buttons)):
        markup.add(InlineKeyboardButton(buttons[index], callback_data=callbacks[index]))
    return markup


def get_order_kb(price: float) -> ReplyKeyboardMarkup:
    """
    Creates in orders navigation keyboard with total price shown
    :param price: Total price of user's orders
    :return: Created keyboard
    """
    order_kb = ReplyKeyboardMarkup(resize_keyboard=True)
    to_pay: str = f" {price} ".join(ru.CMD_ORDER)
    order_kb.row(KeyboardButton(ru.CMD_BACK), KeyboardButton(ru.CMD_DEL_ORDERS), KeyboardButton(to_pay))
    order_kb.add(KeyboardButton(ru.CMD_SHOW_MY_PAYMENTS))
    return order_kb
