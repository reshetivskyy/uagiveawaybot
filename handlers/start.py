from aiogram import F, Router, html
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select

from db.models import Giveaway, GiveawayUser, Referral, User
from keyboards.inline import get_homepage_keyboard

from db.session import async_session

router = Router()


@router.message(CommandStart())
async def start(message: Message, command: CommandObject):
    async with async_session() as session:
        result = await session.execute(
            select(User).where(User.user_id == message.from_user.id)
        )
        user = result.scalars().first()
        if not user:
            user = User(user_id=message.from_user.id)
            session.add(user)
            await session.flush()
            await session.commit()

    args = command.args
    if not args:
        await message.answer(
            "Привіт! Це перший український бот для розіграшів у Telegram!\n",
            reply_markup=get_homepage_keyboard(),
        )
    else:
        parts = command.args.split("_")
        match parts:
            case ["ga", giveaway_id]:
                async with async_session() as session:
                    result = await session.execute(
                        select(Giveaway).where(Giveaway.id == int(giveaway_id))
                    )
                    giveaway = result.scalars().first()

                    if not giveaway:
                        await message.answer("Розіграш не знайдено.")
                        return

                    if giveaway.creator.user_id == user.user_id:
                        await message.answer(
                            "Ти не можеш приєднатись до власного розіграшу."
                        )
                        return

                    result = await session.execute(
                        select(GiveawayUser).where(
                            GiveawayUser.giveaway_id == giveaway.id,
                            GiveawayUser.user_id == user.id,
                        )
                    )
                    exists = result.scalars().first()

                    if not exists:
                        session.add(
                            GiveawayUser(giveaway_id=giveaway.id, user_id=user.id)
                        )
                        await session.commit()

                        await message.answer(
                            f"Ти успішно приєднався до розіграшу: {html.bold(giveaway.title)}!\n\n"
                            f"{giveaway.response}\n\n"
                            f"Це твоє реферальне посилання: https://t.me/{(await message.bot.get_me()).username}?start=ref_{giveaway.id}_{message.from_user.id}\n"
                        )
                    else:
                        await message.answer("Ти вже приєднався до цього розіграшу.")

            case ["ref", giveaway_id, referrer_id]:
                async with async_session() as session:
                    result = await session.execute(
                        select(Giveaway).where(Giveaway.id == giveaway_id)
                    )

                    giveaway = result.scalars().first()
                    if not giveaway:
                        await message.answer("Розіграш не знайдено.")
                        return

                    if giveaway.creator.user_id == user.user_id:
                        await message.answer(
                            "Ти не можеш приєднатись до власного розіграшу."
                        )

                    result = await session.execute(
                        select(User).where(User.user_id == int(referrer_id))
                    )
                    referrer = result.scalars().first()
                    if not referrer:
                        await message.answer("Айді реферера не знайдено.")
                        return

                    result = await session.execute(
                        select(GiveawayUser).where(
                            GiveawayUser.giveaway_id == giveaway.id,
                            GiveawayUser.user_id == user.id,
                        )
                    )
                    exists = result.scalars().first()

                    if not exists:
                        session.add(
                            GiveawayUser(giveaway_id=giveaway.id, user_id=user.id)
                        )

                        if referrer.id != user.id:
                            referral = Referral(
                                giveaway_id=giveaway.id,
                                referrer_id=referrer.id,
                                referred_id=user.id,
                            )
                            session.add(referral)

                        await session.commit()

                        await message.bot.send_message(
                            referrer.user_id,
                            f"Хтось приєднався до розіграшу: {html.bold(giveaway.title)} за твоїм реферальним посиланням.",
                        )

                        await message.answer(
                            f"Ти успішно приєднався до розіграшу: {html.bold(giveaway.title)} за реферальним посиланням.\n"
                            f"{giveaway.response}\n"
                        )
                    else:
                        await message.answer("Ти вже приєднався до цього розіграшу.")


@router.callback_query(F.data == "homepage")
async def homepage(callback_query: CallbackQuery):
    await callback_query.answer()
    await callback_query.message.answer(
        "Це перший український бот для розіграшів у Telegram!\nМеню:",
        reply_markup=get_homepage_keyboard(),
    )
