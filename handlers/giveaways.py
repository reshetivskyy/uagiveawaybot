

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload

from db.models import Giveaway, GiveawayUser, Referral, User
from db.session import async_session
from keyboards.inline import get_giveaway_keyboard, get_homepage_keyboard
from states.giveaway import EditGiveawayStates
from utils.formatters import format_giveaway_text, format_joined_giveaway_text


router = Router()

@router.callback_query(F.data == "create_giveaway")
async def create_giveaway(callback_query: CallbackQuery):
    await callback_query.answer()
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == callback_query.from_user.id)
        )
        user = result.scalars().first()

        giveaway = Giveaway(title="", response="", sharing=False, creator=user)
        session.add(giveaway)

        await session.flush()
        await session.refresh(giveaway)

        await session.commit()

    await callback_query.message.edit_text(
        await format_giveaway_text(giveaway, callback_query), reply_markup=get_giveaway_keyboard(giveaway)
    )

@router.callback_query(F.data.startswith("edit_giveaway_title:"))
async def edit_giveaway_title(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    giveaway_id = int(callback_query.data.split(":")[1])
    await state.update_data(giveaway_id=giveaway_id)

    await state.set_state(EditGiveawayStates.waiting_for_title)
    await callback_query.message.answer("Напиши свою назву для розіграшу.")


@router.callback_query(F.data.startswith("edit_giveaway_response:"))
async def edit_giveaway_response(callback_query: CallbackQuery, state: FSMContext):
    await callback_query.answer()

    giveaway_id = int(callback_query.data.split(":")[1])
    await state.update_data(giveaway_id=giveaway_id)

    await state.set_state(EditGiveawayStates.waiting_for_response)
    await callback_query.message.answer(
        "Напиши своє повідомлення яке побачить користувач коли візьме участь в розіграші."
    )

@router.message(EditGiveawayStates.waiting_for_title)
async def waiting_for_title(message: Message, state: FSMContext):
    value = message.text
    data = await state.get_data()
    giveaway_id = data["giveaway_id"]
    
    async with async_session() as session:
        giveaway = await session.get(Giveaway, giveaway_id)
        giveaway.title = value

        await session.commit()

    await message.answer("Назву розіграшу успішно змінено!")
    await state.clear()

@router.message(EditGiveawayStates.waiting_for_response)
async def waiting_for_response(message: Message, state: FSMContext):
    value = message.text
    data = await state.get_data()
    giveaway_id = data["giveaway_id"]

    async with async_session() as session:
        giveaway = await session.get(Giveaway, giveaway_id)
        giveaway.response = value

        await session.commit()

    await message.answer("Відповідь для користувача успішно змінено!")
    await state.clear()

@router.callback_query(F.data.startswith("delete_giveaway:"))
async def delete_giveaway(callback_query: CallbackQuery):
    giveaway_id = int(callback_query.data.split(":")[1])

    async with async_session() as session:
        giveaway = await session.get(Giveaway, giveaway_id)
        await session.delete(giveaway)
        await session.execute(
            delete(Referral).where(Referral.giveaway_id == giveaway_id)
        )
        await session.execute(
            delete(GiveawayUser).where(GiveawayUser.giveaway_id == giveaway_id)
        )
        await session.execute(delete(Giveaway).where(Giveaway.id == giveaway_id))
        await session.commit()

    await callback_query.message.edit_text("Розіграш успішно видалено.")
    await callback_query.message.answer("Це перший український бот для розіграшів у Telegram!\nМеню:", reply_markup=get_homepage_keyboard())

@router.callback_query(F.data == "view_joinedgiveaways")
async def view_joinedgiveaways(callback_query: CallbackQuery):
    await callback_query.answer()

    async with async_session() as session:
        result = await session.execute(
            select(Giveaway)
            .join(GiveawayUser)
            .join(User)
            .where(User.user_id == callback_query.from_user.id)
            .options(selectinload(Giveaway.creator))
        )
        giveaways_list = result.scalars().all()

    if not giveaways_list:
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text="<<<", callback_data="homepage"),
                ]
            ]
        )

        await callback_query.message.edit_text(
            "Ти не береш участі в жодному розіграші.", reply_markup=kb
        )
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [
                    InlineKeyboardButton(
                        text=f"#{g.id} - {g.title}",
                        callback_data=f"view_joined_giveaway:{g.id}",
                    )
                ]
                for g in giveaways_list
            ],
            [
                InlineKeyboardButton(text="<<<", callback_data="homepage"),
            ],
        ]
    )

    await callback_query.message.edit_text("Твої розіграші:", reply_markup=kb)


@router.callback_query(F.data == "view_giveaways")
async def view_giveaways(callback_query: CallbackQuery):
    await callback_query.answer()

    async with async_session() as session:
        result = await session.execute(
            select(User)
            .options(selectinload(User.created_giveaways))
            .where(User.user_id == callback_query.from_user.id)
        )
        user = result.scalars().first()
        giveaways_list = user.created_giveaways if user else []

    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="<<<", callback_data="homepage")]]
    )

    if not giveaways_list:
        await callback_query.message.edit_text(
            "В тебе немає створених розіграшів.", reply_markup=kb
        )
        return

    ITEMS_PER_PAGE = 5
    page = 1
    start = (page - 1) * ITEMS_PER_PAGE
    end = start + ITEMS_PER_PAGE
    sliced = giveaways_list[start:end]

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            *[
                [
                    InlineKeyboardButton(
                        text=f"#{g.id} - {g.title}",
                        callback_data=f"view_giveaway:{g.id}",
                    )
                ]
                for g in sliced
            ],
            [
                InlineKeyboardButton(text="<", callback_data=f"page:{page-1}"),
                InlineKeyboardButton(text=">", callback_data=f"page:{page+1}"),
            ],
            [
                InlineKeyboardButton(text="<<<", callback_data="homepage"),
            ],
        ]
    )

    await callback_query.message.edit_text("Твої розіграші:", reply_markup=kb)

@router.callback_query(F.data.startswith("view_giveaway:"))
async def view_giveaway(callback_query: CallbackQuery):
    await callback_query.answer()
    giveaway_id = int(callback_query.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway).where(Giveaway.id == giveaway_id)
        )
        giveaway = result.scalars().first()

    await callback_query.message.edit_text(
        await format_giveaway_text(giveaway, callback_query), reply_markup=get_giveaway_keyboard(giveaway)
    )

@router.callback_query(F.data.startswith("view_joined_giveaway:"))
async def view_joined_giveaway(callback_query: CallbackQuery):
    await callback_query.answer()
    giveaway_id = int(callback_query.data.split(":")[1])
    async with async_session() as session:
        result = await session.execute(
            select(Giveaway).where(Giveaway.id == giveaway_id)
        )
        giveaway = result.scalars().first()

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="<<<", callback_data="view_joinedgiveaways")]
        ]
    )

    await callback_query.message.edit_text(
        await format_joined_giveaway_text(giveaway, callback_query),
        reply_markup=kb,
    )