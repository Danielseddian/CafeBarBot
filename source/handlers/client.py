from aiogram import Dispatcher
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.dispatcher.filters import Text

from core import config
from core.messanger import respond
from handlers.base import LEVEL, check_user_registration
from keyboards.client_kb import division_kb, kitchen_kb, bar_kb, hookah_kb
from localization import ru


async def start(message: Message) -> None:
    """
    Respond with keyboard of Caffe divisions
    :param message: Aiogram message object
    :return: Shown keyboard of Caffe divisions
    """
    check_user_registration(message.from_user.id)
    LEVEL.top()
    await respond(message, ru.MSG_WELCOME, division_kb)


async def kitchen(message: Message) -> None:
    """
    Respond with keyboard of Kitchen divisions
    :param message: Aiogram message object
    :return: Shown keyboard of Kitchen divisions
    """
    LEVEL.add(start)
    await respond(message, ru.MSG_ENJOY_MEAL, kitchen_kb)


async def bar(message: Message) -> None:
    """
    Respond with keyboard of Bar divisions
    :param message: Aiogram message object
    :return: Shown keyboard of Bar divisions
    """
    LEVEL.add(start)
    await respond(message, ru.MSG_TOAST, bar_kb)


async def hookah(message: Message) -> None:
    """
    Respond with keyboard of Hookah divisions
    :param message: Aiogram message object
    :return: Shown keyboard of Hookah divisions
    """
    LEVEL.add(start)
    await respond(message, ru.MSG_SMOKE, hookah_kb)


async def close_keyboard(message: Message) -> None:
    """
    Hide keyboard
    :param message: Aiogram message object
    :return: Closed keyboard
    """
    LEVEL.nope()
    text = ru.MSG_KB_HIDED + "\n\n" + ru.MSG_GET_ADMIN_KB if message.from_user.id in config.ADMINS else ru.MSG_KB_HIDED
    await respond(message, text, ReplyKeyboardRemove())


async def back(message: Message) -> None:
    """
    Back to the top level of keyboard
    :param message: Aiogram message object
    :return: Backed to the top level
    """
    await LEVEL.up(message)


def reg_division_handlers(dp: Dispatcher) -> None:
    """
    Register Caffe division's handlers in the dispatcher of the bot
    :param dp: Dispatcher of the bot
    :return: Registered handlers
    """
    dp.register_message_handler(start, commands=["start", ru.CMD_START])
    dp.register_message_handler(start, Text(equals=ru.CMD_START, ignore_case=True))
    dp.register_message_handler(kitchen, Text(equals=ru.CMD_KITCHEN, ignore_case=True))
    dp.register_message_handler(bar, Text(equals=ru.CMD_BAR, ignore_case=True))
    dp.register_message_handler(hookah, Text(equals=ru.CMD_HOOKAH, ignore_case=True))
    dp.register_message_handler(close_keyboard, Text(equals=ru.CMD_HIDE_KB, ignore_case=True))
    dp.register_message_handler(back, Text(equals=ru.CMD_BACK, ignore_case=True))
