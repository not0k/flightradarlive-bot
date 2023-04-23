import os
import logging
from typing import Final

from dotenv import load_dotenv
from telegram import Update, Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

import db

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_TOKEN: Final = os.getenv('TELEGRAM_TOKEN')


# Commands

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is not None:
        await update.message.reply_text(
            'You are already receiving notifications!\n'
            'If you want a command list, tap the menu button below.'
        )
        return

    await update.message.reply_text('Send me your location or live location to get started!')


async def stop_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await update.message.reply_text(
            'You are not receiving notifications!\n'
            'Send me your location to start receiving notifications...'
        )
        return

    db.delete_user(user_id)
    await update.message.reply_text(
        'You will no longer receive notifications!\n'
        'Send /start to start receiving notifications again.'
    )


if __name__ == '__main__':
    # Create the application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Command handlers
    app.add_handler(CommandHandler('start', start_command))

    # Start the application
    app.run_polling()
