from aiogram import F, Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from sqlalchemy import select

from db.models import Channel, User
from db.session import async_session

router = Router()


@router.callback_query(F.data == "connect_channel")
async def connect_channel(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Прив'язати канал",
                    url=f"https://t.me/{(await callback_query.bot.get_me()).username}?startchannel",
                )
            ]
        ]
    )

    await callback_query.message.answer(
        "Щоб прив'язати канал натисни на кнопку нижче і проконтролюй щоб бот отримав права на редагування повідомлень!",
        reply_markup=kb,
    )


@router.my_chat_member(F.new_chat_member.status.in_(["administrator", "creator"]))
async def my_chat_member_handler(chat_member: CallbackQuery):
    print(chat_member.model_dump())
    user_id = chat_member.from_user.id
    channel_id = chat_member.chat.id

    async with async_session() as session:
        result = await session.execute(select(User).where(User.user_id == user_id))
        user = result.scalars().first()

        channel = Channel(channel_id=channel_id, owner=user)

        session.add(channel)
        await session.flush()
        user.channels.append(channel)
        await session.commit()

    await chat_member.bot.send_message(
        user_id, "Бот успішно доданий до каналу як адміністратор!"
    )


@router.callback_query(F.data == "disconnect_channel")
async def disconnect_channel(callback_query: CallbackQuery):
    await callback_query.answer()

    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == callback_query.from_user.id)
        )
        user = result.scalars().first()

        if not user or not user.channels:
            await callback_query.message.answer("У тебе немає прив'язаних каналів.")
            return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [
                    InlineKeyboardButton(
                        text=str(channel.channel_id),
                        callback_data=f"disconnect_channel:{channel.id}",
                    )
                ]
                for channel in user.channels
            ],
            [InlineKeyboardButton(text="<<<", callback_data="homepage")],
        ]
    )

    await callback_query.message.edit_text(
        "Оберіть канал для відв'язки:", reply_markup=kb
    )


@router.callback_query(F.data.startswith("disconnect_channel:"))
async def disconnect_channel_callback(callback_query: CallbackQuery):
    await callback_query.answer()
    channel_id = int(callback_query.data.split(":")[1])

    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.id == channel_id))
        channel = result.scalars().first()

        await session.delete(channel)
        await session.commit()

    await callback_query.bot.leave_chat(channel.channel_id)

    await callback_query.message.edit_text("Канал успішно відв'язано.")
