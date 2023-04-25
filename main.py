import os
import logging
import threading
import time
from math import cos, radians
from typing import Final

import FlightRadar24.flight
from dacite import from_dict
from dotenv import load_dotenv
from FlightRadar24.api import FlightRadar24API
from telegram import Update, Message, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, CallbackContext

import db
from user import User

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

TELEGRAM_TOKEN: Final = os.getenv('TELEGRAM_TOKEN')

fr_api: Final = FlightRadar24API()


# Helper functions

def get_bounding_box(latitude: float, longitude: float, radius: int) -> dict[str, float]:
    diameter_km: int = radius // 1000  # meters to kilometers

    return {
        'tl_y': latitude + (diameter_km / 111.32),
        'br_y': latitude - (diameter_km / 111.32),
        'tl_x': longitude - (diameter_km / (111.32 * cos(radians(latitude)))),
        'br_x': longitude + (diameter_km / (111.32 * cos(radians(latitude)))),
    }


def get_img_src(aircraft_images) -> str | None:
    if isinstance(aircraft_images, dict):
        large_images = aircraft_images.get('large', None)
        if isinstance(large_images, list) and len(large_images) > 0:
            image_src = large_images[0].get('src', None)
            return image_src
    return None


def create_message(flight: FlightRadar24.flight.Flight) -> str:
    altitude_m: int = int(flight.altitude * 0.3048)  # feet to meters
    speed_kmh: int = int(flight.ground_speed * 1.852)  # knots to km/h

    origin_airport: str = flight.origin_airport_iata
    origin_country: str = flight.origin_airport_country_name
    destination_airport: str = flight.destination_airport_iata
    destination_country: str = flight.destination_airport_country_name

    origin: str = f'{origin_airport} - {origin_country}' if origin_country != "N/A" else origin_airport
    destination: str = f'{destination_airport} - {destination_country}' if destination_country != "N/A" else destination_airport

    plane_emoji: str = '\N{AIRPLANE}'

    return (
        f'{plane_emoji} New flight in your area {plane_emoji}\n\n'
        f'Aircraft: {flight.registration} ({flight.aircraft_code})\n'
        f'Callsign: {flight.callsign}\n'
        f'Altitude: {altitude_m}m\n'
        f'Speed: {speed_kmh}km/h\n'
        f'From: {origin}\n'
        f'To: {destination}'
    )


async def no_notifications_message(update: Update) -> None:
    await update.message.reply_text(
        'You are not receiving notifications!\n'
        'Send me your location to start receiving notifications...'
    )


# Schedules

def check_flights() -> None:
    while True:
        for user_entry in db.select_users():
            if user_entry is None:
                continue

            user: User = from_dict(data_class=User, data=user_entry)

            bounding_box = get_bounding_box(user.latitude, user.longitude, user.radius)
            bounds = fr_api.get_bounds(bounding_box)
            flights = fr_api.get_flights(bounds=bounds)

            for flight in flights:
                if db.select_flight(user.id, flight.id) is not None:
                    continue

                if flight.altitude < user.min_altitude or flight.altitude > user.max_altitude:
                    continue

                db.insert_flight(user.id, flight.id)

                app.job_queue.run_once(send_notification, 0, user_id=user.id, data=flight)

        time.sleep(5)


async def send_notification(context: CallbackContext) -> None:
    user_id: int = context.job.user_id
    flight: FlightRadar24.flight.Flight = context.job.data

    details: dict = fr_api.get_flight_details(flight.id)
    flight.set_flight_details(details)

    image_src: str = get_img_src(flight.aircraft_images)

    msg: str = create_message(flight)

    tracking_url: str = f'https://www.flightradar24.com/{flight.callsign}/{flight.id}'

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('\N{ROUND PUSHPIN} View on Map', url=tracking_url)
        ]
    ]) if flight.callsign != "N/A" else None

    if image_src:
        await context.bot.send_photo(user_id, image_src, msg, reply_markup=reply_markup)
    else:
        await context.bot.send_message(user_id, msg, reply_markup=reply_markup)


def delete_old_flights() -> None:
    flight_delete_interval: Final = 300  # 5 minutes

    while True:
        db.delete_old_flights(flight_delete_interval)
        time.sleep(flight_delete_interval)


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
    # Starts the thread that checks for flights
    thread1 = threading.Thread(target=check_flights)
    thread1.start()

    # Starts the thread that deletes old flights
    thread2 = threading.Thread(target=delete_old_flights)
    thread2.start()

    # Creates the application
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

    # Starts the application
    app.run_polling()
