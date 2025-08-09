from aiogram import Router, F
from aiogram.types import CallbackQuery

from db.session import async_session

router = Router()


@router.callback_query(F.data.startswith("select_winners:"))
async def select_winners(callback_query: CallbackQuery):
    await callback_query.answer()
    giveaway_id = int(callback_query.data.split(":")[1])

    # async with async_session() as session:
    await callback_query.message.answer("Функція в розробці!")