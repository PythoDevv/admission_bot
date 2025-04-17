from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_panel() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Barchaga xabar yuborish"))
    builder.row(KeyboardButton(text="Admin qo'shish"), KeyboardButton(text="Admin o'chirish"))
    builder.row(KeyboardButton(text="Foydalanuvchilarni eksport qilish"))
    builder.row(KeyboardButton(text="Admin panelini yopish"))
    return builder.as_markup(resize_keyboard=True)

def broadcast_confirmation() -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Yuborish", callback_data="confirm_broadcast"))
    builder.row(InlineKeyboardButton(text="Bekor qilish", callback_data="cancel_broadcast"))
    return builder.as_markup()