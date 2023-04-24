import os
import logging
from typing import Final

from dacite import from_dict
from dotenv import load_dotenv
from telegram import Update, Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

import db
from user import User

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_TOKEN: Final = os.getenv('TELEGRAM_TOKEN')


# Helper functions

async def no_notifications_message(update: Update) -> None:
    await update.message.reply_text(
        'You are not receiving notifications!\n'
        'Send me your location to start receiving notifications...'
    )


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


async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await no_notifications_message(update)
        return

    user: User = from_dict(data_class=User, data=entry)

    msg: str = (
        'You are receiving notifications for flights in your area.\n'
        '\n'
        f'Radius: {user.radius}m\n'
        f'Altitude Range: {user.min_altitude}m - {user.max_altitude}m'
    )

    await update.message.reply_text(msg)


async def radius_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await no_notifications_message(update)
        return

    user: User = from_dict(data_class=User, data=entry)

    if len(context.args) == 0:
        await update.message.reply_text(
            f'Your current radius is {user.radius}m.\n'
            'Send /radius <radius> to change it.'
        )
        return

    try:
        radius: int = int(context.args[0])
    except ValueError:
        await update.message.reply_text('Radius must be an integer.')
        return

    if radius <= 0:
        await update.message.reply_text('Radius must be greater than 0m.')
        return

    user.radius = radius
    db.update_user(user)
    await update.message.reply_text(f'Your radius has been set to {user.radius}m.')


async def altitude_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await no_notifications_message(update)
        return

    user: User = from_dict(data_class=User, data=entry)

    if len(context.args) == 1:
        try:
            altitude: int = int(context.args[0])
        except ValueError:
            await update.message.reply_text('Altitude must be an integer.')
            return

        if altitude < 0 or altitude > 100000:
            await update.message.reply_text('Altitude must be between 0 and 100000m.')
            return

        user.min_altitude = altitude
        user.max_altitude = altitude

    if len(context.args) == 2:
        try:
            min_altitude: int = int(context.args[0])
        except ValueError:
            await update.message.reply_text('Min altitude must be an integer.')
            return

        try:
            max_altitude: int = int(context.args[1])
        except ValueError:
            await update.message.reply_text('Max altitude must be an integer.')
            return

        if min_altitude > max_altitude:
            await update.message.reply_text('Min altitude must be less than max altitude.')
            return
        if min_altitude < 0 or min_altitude > 100000:
            await update.message.reply_text('Min altitude must be between 0 and 100000m.')
            return
        if max_altitude < 0 or max_altitude > 100000:
            await update.message.reply_text('Max altitude must be between 0 and 100000m.')
            return

        user.min_altitude = min_altitude
        user.max_altitude = max_altitude

    db.update_user(user)

    await update.message.reply_text(
        'Your current altitude range is:\n'
        '\n'
        f'Min: {user.min_altitude}m\n'
        f'Max: {user.max_altitude}m\n'
        '\n'
        'You can change it with:\n'
        '/altitude <altitude>\n'
        '/altitude <min-altitude> <max-atlitude>\n'
        '/altmin <min-altitude>\n'
        '/altmax <max-altitude>'
    )


async def min_altitude_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await no_notifications_message(update)
        return

    user: User = from_dict(data_class=User, data=entry)

    if len(context.args) == 0:
        await update.message.reply_text(
            f'Your current min altitude is {user.min_altitude}m.\n'
            'Send /altmin <altitude> to change it.'
        )
        return

    try:
        min_altitude: int = int(context.args[0])
    except ValueError:
        await update.message.reply_text('Min altitude must be an integer.')
        return

    if min_altitude < 0 or min_altitude > 100000:
        await update.message.reply_text('Min altitude must be between 0 and 100000m.')
        return
    if min_altitude > user.max_altitude:
        await update.message.reply_text(
            'Min altitude must be less than max altitude!'
            f'Your current max altitude is {user.max_altitude}m.'
        )
        return

    user.min_altitude = min_altitude
    db.update_user(user)
    await update.message.reply_text(f'Your min altitude has been set to {user.min_altitude}m.')


async def max_altitude_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        await no_notifications_message(update)
        return

    user: User = from_dict(data_class=User, data=entry)

    if len(context.args) == 0:
        await update.message.reply_text(
            f'Your current max altitude is {user.max_altitude}m.\n'
            'Send /altmax <altitude> to change it.'
        )
        return

    try:
        max_altitude: int = int(context.args[0])
    except ValueError:
        await update.message.reply_text('Max altitude must be an integer.')
        return

    if max_altitude < 0 or max_altitude > 100000:
        await update.message.reply_text('Max altitude must be between 0 and 100000m.')
        return
    if max_altitude < user.min_altitude:
        await update.message.reply_text('Max altitude must be greater than min altitude!')
        return

    user.max_altitude = max_altitude
    db.update_user(user)
    await update.message.reply_text(f'Your max altitude has been set to {max_altitude}m.')


# Messages

async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message: Message = update.message or update.edited_message
    user_id: int = update.effective_user.id

    entry = db.select_user(user_id)
    if entry is None:
        new_user = User(id=user_id, latitude=message.location.latitude, longitude=message.location.longitude)
        db.insert_user(new_user)
        await message.reply_text('You are now receiving notifications!')
        return

    user: User = from_dict(data_class=User, data=entry)

    user.latitude = message.location.latitude
    user.longitude = message.location.longitude

    db.update_user(user)

    if not update.edited_message:
        await update.message.reply_text('Your location has been updated!')


if __name__ == '__main__':
    # Create the application
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Message handlers
    app.add_handler(MessageHandler(filters.LOCATION, handle_location))

    # Command handlers
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('stop', stop_command))
    app.add_handler(CommandHandler('info', info_command))
    app.add_handler(CommandHandler('radius', radius_command))
    app.add_handler(CommandHandler('altitude', altitude_command))
    app.add_handler(CommandHandler('altmin', min_altitude_command))
    app.add_handler(CommandHandler('altmax', max_altitude_command))

    # Start the application
    app.run_polling()
