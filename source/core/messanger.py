from typing import Union

from aiogram import Bot
from aiogram.types import Message, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup, CallbackQuery
from aiogram.utils import exceptions as aiogram_exceptions
from core.create import bot
from localization import ru

MARKUPS = Union[ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardMarkup]
RESPONSE = Union[Bot, None]
MESSAGES = Union[Message, CallbackQuery]


async def respond(message: MESSAGES, text, markup: MARKUPS = None, del_msg=True) -> RESPONSE:
    """
    Sends private message to the message's author or warn about subscribing
    :param message: Aiogram message object
    :param text: Text of message for sending
    :param markup: Keyboard markup for running keyboard
    :param del_msg: If del_msg delete message
    :return: Sent message to the message's author
    """
    try:
        response = await bot.send_message(message.from_user.id, text, reply_markup=markup, parse_mode="Markdown")
        if del_msg:
            if isinstance(message, CallbackQuery):
                await message.message.delete()
            else:
                await message.delete()
        return response
    except aiogram_exceptions.CantInitiateConversation:
        await message.reply(ru.ERR_NOT_REG)
    except aiogram_exceptions.BotBlocked:
        await message.reply(ru.ERR_BLOCKED)


async def respond_with_photo(message: MESSAGES, img: str, text: str, markup: MARKUPS = None, del_msg=True) -> RESPONSE:
    """
    Sends private message to the message's author or warn about subscribing
    :param message: Aiogram message object
    :param img: Photo id for sending
    :param text: Text of message for sending
    :param markup: Keyboard markup for running keyboards
    :param del_msg: If del_msg delete message
    :return: Sent message to the message's author
    """
    try:
        response = await bot.send_photo(message.from_user.id, img, text, reply_markup=markup, parse_mode="Markdown")
        if del_msg:
            if isinstance(message, CallbackQuery):
                await message.message.delete()
            else:
                await message.delete()
        return response
    except aiogram_exceptions.CantInitiateConversation:
        await message.reply(ru.ERR_NOT_REG)
    except aiogram_exceptions.BotBlocked:
        await message.reply(ru.ERR_BLOCKED)


async def respond_file(message: MESSAGES, f_path: str, del_msg=True) -> RESPONSE:
    """
    Sends private message to the message's author or warn about subscribing
    :param message: Aiogram message object
    :param f_path: File path to send
    :param del_msg: If del_msg delete message
    :return: Sent message to the message's author
    """
    try:
        with open(f_path, "rb") as file:
            response = await bot.send_document(message.from_user.id, document=file)
        if del_msg:
            if isinstance(message, CallbackQuery):
                await message.message.delete()
            else:
                await message.delete()
        return response
    except aiogram_exceptions.CantInitiateConversation:
        await message.reply(ru.ERR_NOT_REG)
    except aiogram_exceptions.BotBlocked:
        await message.reply(ru.ERR_BLOCKED)
