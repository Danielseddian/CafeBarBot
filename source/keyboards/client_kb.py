from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from localization import ru
from keyboards.base_kb import append_kitchen_kb, append_bar_kb, append_hookah_kb, append_base_kb

division_kb = ReplyKeyboardMarkup(resize_keyboard=True)
division_kb.row(KeyboardButton(ru.CMD_KITCHEN), KeyboardButton(ru.CMD_BAR), KeyboardButton(ru.CMD_HOOKAH))
append_base_kb(division_kb)

kitchen_kb = append_kitchen_kb(ReplyKeyboardMarkup(resize_keyboard=True))
append_base_kb(kitchen_kb)

bar_kb = append_bar_kb(ReplyKeyboardMarkup(resize_keyboard=True))
append_base_kb(bar_kb)

hookah_kb = append_hookah_kb(ReplyKeyboardMarkup(resize_keyboard=True))
append_base_kb(hookah_kb)

base_kb = append_base_kb(ReplyKeyboardMarkup(resize_keyboard=True))
