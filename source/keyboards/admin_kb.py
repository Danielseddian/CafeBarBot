from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from localization import ru
from keyboards.base_kb import append_categories_kb

# -------------------------------------------------------------------------------------------------------------------- #
# Main keyboard                                                                                                        #
# -------------------------------------------------------------------------------------------------------------------- #
admin_kb = ReplyKeyboardMarkup(resize_keyboard=True)
admin_kb.add(KeyboardButton(ru.CMD_UPD_MENU)).add(KeyboardButton(ru.CMD_UPD_ORDERS)).add(KeyboardButton(ru.CMD_HIDE_KB))
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Menu's keyboards                                                                                                     #
# -------------------------------------------------------------------------------------------------------------------- #
upd_menu_kb = ReplyKeyboardMarkup(resize_keyboard=True)
upd_menu_kb.row(KeyboardButton(ru.CMD_CHANGE), KeyboardButton(ru.CMD_DELETE), KeyboardButton(ru.CMD_ADD))
upd_menu_kb.row(KeyboardButton(ru.CMD_HIDE_KB), KeyboardButton(ru.CMD_BACK))

add_kb = append_categories_kb(ReplyKeyboardMarkup(resize_keyboard=True)).add(KeyboardButton(ru.CMD_CANCEL))

change_kb = append_categories_kb(ReplyKeyboardMarkup(resize_keyboard=True)).add(KeyboardButton(ru.CMD_CANCEL))

delete_kb = append_categories_kb(ReplyKeyboardMarkup(resize_keyboard=True)).add(KeyboardButton(ru.CMD_CANCEL))

cancel_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(ru.CMD_CANCEL))

back_kb = ReplyKeyboardMarkup(resize_keyboard=True).add(KeyboardButton(ru.CMD_BACK))
# -------------------------------------------------------------------------------------------------------------------- #

# -------------------------------------------------------------------------------------------------------------------- #
# Shift's keyboards                                                                                                    #
# -------------------------------------------------------------------------------------------------------------------- #
shift_kb = ReplyKeyboardMarkup(resize_keyboard=True)
shift_kb.row(
    KeyboardButton(ru.CMD_ADMIN_REPORT), KeyboardButton(ru.CMD_ADMIN_FND_PAYMENT), KeyboardButton(ru.CMD_SHOW_PAID)
)
shift_kb.row(KeyboardButton(">"), KeyboardButton(ru.CMD_ADMIN_CLS_SHIFT), KeyboardButton("<"))
shift_kb.row(KeyboardButton(ru.CMD_HIDE_KB), KeyboardButton(ru.CMD_BACK))
# -------------------------------------------------------------------------------------------------------------------- #
