import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import (
    Message, WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
)
from dotenv import load_dotenv

from aiogram.filters import CommandStart
from aiogram import Router

router = Router()

buttons = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(
            text='ЗДЕСЬ WEBAPP!',
            web_app=WebAppInfo(url='https://vpntelegram.ru')
        )]
    ]
)


@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    """This handler receives messages with `/start` command."""
    await message.answer(
        f"Hello, {message.from_user.full_name}!",
        reply_markup=buttons
    )

load_dotenv()
TOKEN = os.getenv('BOT_TOKEN')

bot = Bot(TOKEN)
dp = Dispatcher()


async def main() -> None:
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit!')
