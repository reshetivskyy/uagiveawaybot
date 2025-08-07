from aiogram import html

async def format_giveaway_text(giveaway, callback_query):
    return (
        f"Назва розіграшу: {giveaway.title}\n"
        f"Текст для користувача: {giveaway.response}\n"
        f"Чи обов'язкове запрошення друга?: {giveaway.sharing}\n"
        f"\n"
        f"Посилання на розіграш: https://t.me/{(await callback_query.bot.get_me()).username}?start=ga_{giveaway.id}\n"
    )

async def format_joined_giveaway_text(giveaway, callback_query):
    return (
        f"Розіграш: {html.bold(giveaway.title)}\n"
        f"\n{giveaway.response}\n"
        f"\n"
        f"Реферальне посилання: https://t.me/{(await callback_query.bot.get_me()).username}?start=ref_{giveaway.id}_{callback_query.from_user.id}"
    )
