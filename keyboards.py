from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton, InlineKeyboardMarkup

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Начать Игру №1")]
], resize_keyboard=True, one_time_keyboard=True)

keyboard_options = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="A", callback_data="a")],
            [InlineKeyboardButton(text="B", callback_data="b")],
            [InlineKeyboardButton(text="C", callback_data="c")],
            [InlineKeyboardButton(text="D", callback_data="d")]
        ]
)


