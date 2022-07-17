from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.dispatcher.filters import Text

from core.config import ADMINS
from core.messanger import respond
from database import sql_db
from handlers.base import (
    LEVEL,
    FSMAdd,
    FSMCng,
    FSMDel,
    check_category,
    check_menu,
    change_or_create_position,
    delete_position,
    show_menu,
)
from localization import ru
from keyboards.admin_kb import upd_menu_kb, add_kb, change_kb, delete_kb, cancel_kb, back_kb, admin_kb
from keyboards.base_kb import make_inline_buttons


async def check_admin(message: Message) -> None:
    """
    Checks user is group's admin and returns admin keyboard
    :param message: Aiogram message object
    :return: Shown admin keyboard
    """
    LEVEL.top()
    if message.from_user.id in ADMINS:
        await respond(message, ru.MSG_ADMIN_CHECKED, admin_kb)


async def update_menu(message: Message) -> None:
    """
    Shows menu's updating keyboard
    :param message: Aiogram message object
    :return: Shown menu's updating keyboard
    """
    LEVEL.add(check_admin)
    if message.from_user.id in ADMINS:
        await respond(message, ru.MSG_ADMIN_UPD_MENU, upd_menu_kb)


# -------------------------------------------------------------------------------------------------------------------- #
# Add menu's position functions                                                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
async def choose_add_category(message: Message, state: FSMContext = None) -> None:
    """
    Asks category for new menu's position
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Requested product's category and shown select keyboard
    """
    LEVEL.add(update_menu)
    if message.from_user.id in ADMINS:
        await FSMAdd.category.set()
        await respond(message, ru.MSG_ADMIN_ADD, add_kb)


async def set_category(message: Message, state: FSMContext) -> None:
    """
    Sets up category and asks image of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up image and sent ask of name
    """
    if message.from_user.id in ADMINS:
        category_name: str = message.text
        if category_name != "-":
            category: str = await check_category(message)
            if not category:
                await message.reply(ru.ERR_NO_CATEGORY)
                return
            async with state.proxy() as data:
                data["category"] = category
        else:
            async with state.proxy() as data:
                category_name: str = data.get("category", "")
                if not category_name:
                    await message.reply(ru.ERR_NO_CATEGORY)
                    return
        await FSMAdd.next()
        await respond(message, ru.MSG_ADMIN_ADD_IMAGE.format(category_name), cancel_kb, del_msg=False)
    else:
        await state.finish()


async def set_image(message: Message, state: FSMContext) -> None:
    """
    Sets up photo and asks name of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up image and sent ask of name
    """
    if message.from_user.id in ADMINS:
        if message.text != "-":
            if message.content_type != "photo":
                await message.reply(ru.ERR_NOT_IMG)
                return
            async with state.proxy() as data:
                data["image"] = message.photo[0].file_id
        else:
            async with state.proxy() as data:
                if not data.get("image"):
                    await message.reply(ru.ERR_NOT_IMG)
                    return
        await FSMAdd.next()
        await respond(message, ru.MSG_ADMIN_ADD_NAME, cancel_kb, del_msg=False)
    else:
        await state.finish()


async def set_name(message: Message, state: FSMContext) -> None:
    """
    Sets up name and asks description of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up name and sent ask of description
    """
    if message.from_user.id in ADMINS:
        name: str = message.text
        if name != "-":
            if sql_db.check_product_name(name):
                await message.reply(ru.ERR_NAME_EXISTS)
                return
            if len(name) > 25:
                await message.reply(ru.ERR_NAME_TOO_LONG)
                return
            async with state.proxy() as data:
                old_name: str = data.get("name", "")
                if old_name and old_name != name:
                    data["old_name"] = old_name
                data["name"] = name
        else:
            async with state.proxy() as data:
                if not data.get("name"):
                    await message.reply(ru.ERR_NAME_NOT_NULL)
                    return
        await FSMAdd.next()
        await respond(message, ru.MSG_ADMIN_ADD_DESCRIPTION, cancel_kb, del_msg=False)
    else:
        await state.finish()


async def set_description(message: Message, state: FSMContext) -> None:
    """
    Sets up description and asks price of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up description and sent ask of price
    """
    if message.from_user.id in ADMINS:
        description: str = message.text
        if description != "-":
            if 500 > len(description) < 50:
                await message.reply(ru.ERR_CATEGORY_LEN)
                return
            async with state.proxy() as data:
                data["description"] = description
        else:
            async with state.proxy() as data:
                if not data.get("description"):
                    await message.reply(ru.ERR_CATEGORY_LEN)
                    return
        await FSMAdd.next()
        await respond(message, ru.MSG_ADMIN_ADD_PRICE, cancel_kb, del_msg=False)
    else:
        await state.finish()


async def set_price(message: Message, state: FSMContext) -> None:
    """
    Sets up price and asks count of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up price
    """
    if message.from_user.id in ADMINS:
        price: str = message.text
        if price != "-":
            price: str = price.replace(",", ".", 1)
            if not price.replace(".", "", 1).isdigit():
                await message.reply(ru.ERR_NOT_NUM)
                return
            price: float = round(float(price), 2)
            async with state.proxy() as data:
                data["price"] = price
        else:
            async with state.proxy() as data:
                if not data.get("price"):
                    await message.reply(ru.ERR_NOT_NUM)
                    return
        await FSMAdd.next()
        await respond(message, ru.MSG_ADMIN_ADD_COUNT, cancel_kb, del_msg=False)
    else:
        await state.finish()


async def set_count(message: Message, state: FSMContext) -> None:
    """
    Sets up price and asks count of product
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Set up price
    """
    if message.from_user.id in ADMINS:
        count: str = message.text
        if count != "-":
            if not count.isdigit():
                await message.reply(ru.ERR_NOT_NUM)
                return
            count: int = int(count)
            async with state.proxy() as data:
                data["count"] = count
                data: dict = dict(**data)
        else:
            async with state.proxy() as data:
                count: int = data.get("count")
                data: dict = dict(**data)
                if not count:
                    await message.reply(ru.ERR_NOT_NUM)
                    return
        await state.finish()
        await change_or_create_position(data, message, data.pop("old_name", ""))
        await update_menu(message)
    else:
        await state.finish()


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Change menu's position functions                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
async def choose_change_category(message: Message) -> None:
    """
    Asks category for update menu's position
    :param message: Aiogram message object
    :return: Requested product's category and shown select keyboard
    """
    LEVEL.add(update_menu)
    if message.from_user.id in ADMINS:
        await FSMCng.category.set()
        await respond(message, ru.MSG_ADMIN_CHANGE, change_kb)


async def choose_change_position(message: Message, state: FSMContext) -> None:
    """
    Shows category's positions and change inline buttons
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Shown category's positions and change buttons
    """
    if message.from_user.id in ADMINS:
        menu: list = await check_menu(message, await check_category(message), state)
        if menu:
            await show_menu(menu, message, ru.NLN_CHANGE, "change {}", admin=True)
            await respond(message, ru.MSG_ADMIN_CHANGE_ATTENTION, back_kb, del_msg=False)
    else:
        await state.finish()


async def change_position(query: CallbackQuery, state: FSMContext = None) -> None:
    """
    Delete dish from menu database
    :param query: Aiogram query object
    :param state: Aiogram FSMContext
    :return: Deleted dish from menu
    """
    if query.from_user.id in ADMINS:
        name: str = query.data.replace("change ", "")
        await FSMAdd.category.set()
        async with state.proxy() as data:
            data.update(dict(zip(sql_db.get_product_fields(), sql_db.get_product(name))))
        await respond(query, ru.MSG_ADMIN_CHANGE_CATEGORY, add_kb)


# -------------------------------------------------------------------------------------------------------------------- #


# -------------------------------------------------------------------------------------------------------------------- #
# Delete menu's position functions                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
async def choose_delete_category(message: Message, state: FSMContext = None) -> None:
    """
    Asks category for delete menu's position
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Requested product's category and shown select keyboard
    """
    LEVEL.add(update_menu)
    if message.from_user.id in ADMINS:
        await FSMDel.category.set()
        await respond(message, ru.MSG_ADMIN_DELETE, delete_kb)


async def choose_del_position(message: Message, state: FSMContext) -> None:
    """
    Shows category's positions and delete inline button
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :return: Shown category's positions and delete buttons
    """
    if message.from_user.id in ADMINS:
        menu: list = await check_menu(message, await check_category(message), state)
        if menu:
            await show_menu(menu, message, ru.NLN_DELETE, "del {}", admin=True)
            await respond(message, ru.MSG_ADMIN_DELETE_ATTENTION, back_kb, del_msg=False)
    else:
        await state.finish()


async def ask_del_confirmation(query: CallbackQuery) -> None:
    """
    Asks confirmation to delete a dish from menu database
    :param query: Aiogram query object
    :return: Asked confirmation
    """
    if query.from_user.id in ADMINS:
        name: str = query.data.replace("del ", "")
        markup = make_inline_buttons(
            (ru.NLN_CONFIRM, ru.NLN_CANCEL),
            (f"conf_adm_del{name}", f"decl_adm_del{name}"),
        )
        await respond(query, ru.MSG_ADMIN_CONFIRM.format(name), markup, del_msg=False)


async def del_position(query: CallbackQuery) -> None:
    if query.from_user.id in ADMINS and query.data.startswith("conf_adm_del"):
        name: str = query.data.replace("conf_adm_del", "")
        await delete_position(name, query)
    else:
        await respond(query, ru.MSG_ADMIN_CANCELED, upd_menu_kb)


# -------------------------------------------------------------------------------------------------------------------- #


async def cancel_handler(message: Message, state=FSMContext, text="") -> None:
    """
    Cancels active FSM if user change his mind and sends confirm message
    :param message: Aiogram message object
    :param state: Aiogram FSMContext
    :param text: Alternative text for sending when operation has been canceled
    :return: Canceled FSM and sent confirm message
    """
    if message.from_user.id in ADMINS and await state.get_state():
        await state.finish()
        await respond(message, text or ru.MSG_ADMIN_CANCELED, del_msg=False)
        await LEVEL.up(message)


async def test(message: Message):
    if message.from_user.id in ADMINS:
        await respond(message, "No tasks")


def reg_admin_menu_handlers(dp: Dispatcher) -> None:
    """
    Register admin menu handlers in the dispatcher of the bot
    :param dp: Dispatcher of the bot
    :return: Registered admin menu handlers
    """
    dp.register_message_handler(check_admin, commands=["admin", ru.CMD_ADMIN])
    dp.register_message_handler(check_admin, Text(equals=ru.CMD_ADMIN, ignore_case=True))
    dp.register_message_handler(update_menu, Text(equals=ru.CMD_UPD_MENU, ignore_case=True))
    dp.register_message_handler(choose_add_category, Text(equals=ru.CMD_ADD, ignore_case=True), state=None)
    dp.register_message_handler(choose_change_category, Text(equals=ru.CMD_CHANGE, ignore_case=True), state=None)
    dp.register_message_handler(choose_delete_category, Text(equals=ru.CMD_DELETE, ignore_case=True))
    dp.register_message_handler(cancel_handler, commands=ru.CMD_CANCEL, state="*")
    dp.register_message_handler(cancel_handler, Text(equals=ru.CMD_CANCEL, ignore_case=True), state="*")
    dp.register_message_handler(set_category, state=FSMAdd.category)
    dp.register_message_handler(set_image, content_types=["photo", "text"], state=FSMAdd.image)
    dp.register_message_handler(set_name, state=FSMAdd.name)
    dp.register_message_handler(set_description, state=FSMAdd.description)
    dp.register_message_handler(set_price, state=FSMAdd.price)
    dp.register_message_handler(set_count, state=FSMAdd.count)
    dp.register_message_handler(choose_del_position, state=FSMDel.category)
    dp.register_callback_query_handler(ask_del_confirmation, lambda q: q.data and q.data.startswith("del "))
    dp.register_callback_query_handler(del_position, lambda q: q.data and q.data.startswith("conf_adm_del"))
    dp.register_callback_query_handler(del_position, lambda q: q.data and q.data.startswith("decl_adm_del"))
    dp.register_message_handler(choose_change_position, state=FSMCng.category)
    dp.register_callback_query_handler(change_position, lambda q: q.data and q.data.startswith("change "))
    dp.register_message_handler(test, Text(equals="test", ignore_case=True))
