from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from db.models import Giveaway

def get_giveaway_keyboard(giveaway: Giveaway):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Редагувати назву", callback_data=f"edit_giveaway_title:{giveaway.id}"
                ),
                InlineKeyboardButton(
                    text="Редагувати відповідь", callback_data=f"edit_giveaway_response:{giveaway.id}"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Додати кнопку", callback_data=f"add_button:{giveaway.id}"
                ),
                InlineKeyboardButton(
                    text="Видалити розіграш", callback_data=f"delete_giveaway:{giveaway.id}"
                ),
            ],
            [
                InlineKeyboardButton(text="<<<", callback_data="view_giveaways"),
            ],
        ]
    )


def get_homepage_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Я беру участь", callback_data="view_joinedgiveaways"
                ),
                InlineKeyboardButton(
                    text="Мої розіграші", callback_data="view_giveaways"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Створити розіграш", callback_data="create_giveaway"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Прив'язати канал", callback_data="connect_channel"
                ),
                InlineKeyboardButton(
                    text="Відв'язати канал", callback_data="disconnect_channel"
                ),
            ],
        ]
    )