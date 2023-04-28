# FlightradarLive Bot

## Introduction

FlightradarLive is a Telegram bot that sends real-time flight notifications based on your location and preferences,
using data from the [Flightradar24 API](https://www.flightradar24.com/how-it-works). You can set your notification
radius and altitude range to receive alerts for flights within a specific area, as well as share your live location with
the bot to receive updates on flights in your vicinity. To use FlightradarLive, simply add the bot to your Telegram
account by searching for [@flightradarlive_bot](https://t.me/flightradarlive_bot) and start customizing your
notification settings.

## Usage

The bot supports the following commands:

- `/start`: Initiates the bot and prompts the user to share their location. Once the location is shared, the bot sends
  notifications to the user for flights in their area based on their preferences.

- `/stop`: Stops the user from receiving notifications.

- `/info`: Displays the current notification settings for the user.

- `/radius`: Sets the radius for flight notifications. For example, `/radius 2000` sets the notification radius to 2000
  m. The default radius is 5000 m.

- `/altitude`: Sets the altitude range for flight notifications. The command can be used in two ways:

    - `/altitude <altitude>`: Sets both the minimum and maximum altitude to the specified value.
    - `/altitude <min-altitude> <max-altitude>`: Sets the minimum and maximum altitude to the specified values.

  The default minimum altitude is 0 m and the default maximum altitude is 100000 m.

- `/altmin`: Sets the minimum altitude. For example, `/altmin 1000` sets the minimum
  altitude to 1000 m.

- `/altmax`: Sets the maximum altitude. For example, `/altmax 10000` sets the maximum
  altitude to 10000 m.

Note: Altitude and radius values are measured in meters.

## Requirements

- Python 3.8 or higher

### Required Packages:

This bot was developed using the following package versions:

- `python-dotenv` ~= 1.0.0
- `python-telegram-bot[job-queue]` ~= 20.2
- `FlightRadarAPI` ~= 1.2.7
- `mysql-connector-python` ~= 8.0.33
- `dacite` ~= 1.8.0

To install the required packages, you can use `pip`:

```
pip install -r requirements.txt
```

### External Sources:

- A Telegram bot token
- A MySQL database

## Obtaining a Telegram Bot Token

To obtain a Telegram bot token, follow these steps:

1. Open Telegram and search for the `BotFather` bot.
2. Start a conversation with `BotFather` and send the `/newbot` command.
3. Follow the instructions provided by `BotFather` to create a new bot.
4. `BotFather` will provide you with a token for your bot. Save this token as you will need it later.

## Setting up a MySQL Database

To set up a MySQL database, follow these steps:

1. Install MySQL on your system, if it is not already installed. You can find instructions on how to do this on
   the [MySQL website](https://dev.mysql.com/downloads/installer/).
2. Use the `flightradarbot.sql` script located in the `mysql` directory of the project to create the necessary database
   and tables.
3. Create a new user for the bot to use, and grant the user all privileges on the database.

## Configuration

Before running the bot, you need to set up a `.env` file in the root
directory of the project with your own values. A sample `.env.example` file is provided to show the expected layout of
the file:

```
TELEGRAM_TOKEN=YOUR-TELEGRAM-TOKEN

DB_HOST=YOUR-DB-HOST
DB_PORT=YOUR-DB-PORT
DB_USER=YOUR-DB-USER
DB_PASSWORD=YOUR-DB-PASSWORD
DB_DATABASE=YOUR-DB-DATABASE
```

Replace the placeholders `YOUR-TELEGRAM-TOKEN`, `YOUR-DB-HOST`, `YOUR-DB-PORT`, `YOUR-DB-USER`, `YOUR-DB-PASSWORD`,
and `YOUR-DB-DATABASE` with the appropriate values for your Telegram bot token and MySQL database connection
information.

## Running the Bot

To run the bot, execute the following command:

```
python main.py
```