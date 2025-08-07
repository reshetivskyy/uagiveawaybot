
from aiogram import F, Router
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from sqlalchemy import select


from db.session import async_session
from db.models import Giveaway, User

from states.giveaway import SetChannelStates

router = Router()



@router.callback_query(F.data.startswith("add_button:"))
async def add_button(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == callback_query.from_user.id))
        user = result.scalars().first()

        if not user.channels:
            await callback_query.message.answer("В тебе немає прив'язаних каналів!")
            return

    giveaway_id = int(callback_query.data.split(":")[1])
    await state.update_data(giveaway_id=giveaway_id)
    await state.set_state(SetChannelStates.waiting_for_channel)
    await callback_query.message.answer(
        "Перешли сюди повідомлення або посиланя на повідомлення до якого хочеш додати кнопку з розіграшем."
    )

@router.message(SetChannelStates.waiting_for_channel)
async def handle_channel_message(message: Message, state: FSMContext):
    if message.forward_from_chat:
        await state.update_data(message_id=message.forward_from_message_id, chat_id=message.forward_from_chat.id)
    elif message.text and "t.me/" in message.text:
        try:
            parts = message.text.split("/")
            chat_username = parts[-2]
            message_id = int(parts[-1])
            chat = await message.bot.get_chat(chat_username)
            await state.update_data(message_id=message_id, chat_id=chat.id)
        except Exception:
            await message.answer("Неможливо обробити посилання. Перевір правильність.")
            return
    else:
        await message.answer("Надішли посилання на повідомлення або перешли саме повідомлення.")
        return

    await state.set_state(SetChannelStates.waiting_for_text)
    await message.answer("Введи текст кнопки, яку хочеш додати.")

@router.message(SetChannelStates.waiting_for_text)
async def process_waiting_for_text(message: Message, state: FSMContext):
    data = await state.get_data()
    giveaway_id = data["giveaway_id"]
    message_id = data["message_id"]
    chat_id = data["chat_id"]
    button_text = message.text
    
    async with async_session() as session:
        giveaway = await session.get(Giveaway, giveaway_id)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=button_text, url=f"https://t.me/{(await message.bot.get_me()).username}/?start=ga_{giveaway.id}")]
        ]
    )

    await message.bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=kb
    )
    await message.answer("Кнопку успішно додано ✅")

    await state.clear()