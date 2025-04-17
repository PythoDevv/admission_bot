from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton

def main_menu() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Ariza topshirish"))
    builder.row(KeyboardButton(text="Biz haqimizda"))
    return builder.as_markup(resize_keyboard=True)

def cancel_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="Bekor qilish")]],
        resize_keyboard=True
    )

def passport_choice() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Pasport yuklash"))
    builder.row(KeyboardButton(text="Pasport olaman"))
    builder.row(KeyboardButton(text="Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)

def confirm_application_keyboard() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="✅ Tasdiqlash", callback_data="confirm_application"))
    builder.row(InlineKeyboardButton(text="❌ Qayta yozish", callback_data="restart_application"))
    return builder.as_markup()