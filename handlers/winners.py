from aiogram import Router, F
from aiogram.types import CallbackQuery

from sqlalchemy import select

from db.session import async_session
from db.models import User, GiveawayUser

router = Router()


@router.callback_query(F.data.startswith("select_winners:"))
async def select_winners(callback_query: CallbackQuery):
    await callback_query.answer()
    giveaway_id = int(callback_query.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(
            select(User)
            .join(GiveawayUser, User.id == GiveawayUser.user_id)
            .where(GiveawayUser.giveaway_id == giveaway_id)
        )
        users = result.scalars().all()

    winners_info = []
    for user in users:
        try:
            chat = await callback_query.bot.get_chat(user.user_id)
            if chat.username:
                winners_info.append(f"@{chat.username}")
            else:
                winners_info.append(chat.full_name)
        except Exception:
            winners_info.append(f"[Unknown user {user.user_id}]")

    message_text = "Список переможців:\n" + "\n".join(winners_info)
    await callback_query.message.answer(message_text)

