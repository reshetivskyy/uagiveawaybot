import logging
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Update

logging.basicConfig(level=logging.DEBUG)

router = Router()


@router.errors()
async def on_error(update: Update, exception: Exception):
    try:
        dump = update.model_dump_json(indent=2, exclude_none=True)
    except Exception:
        dump = str(update)
    logging.exception("Unhandled exception while processing update:\n%s", dump)
    return True
