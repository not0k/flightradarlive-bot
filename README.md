# FlightradarLive Bot

## Introduction

FlightradarLive is a Telegram bot that uses the [Flightradar24 API](https://www.flightradar24.com/how-it-works) to send
real-time flight notifications to users based on their location and preferences. Users can set their notification radius
and altitude range to receive alerts for flights within a specific area. You can add the bot to your Telegram by
searching for [@flightradarlive_bot](https://t.me/flightradarlive_bot).

## Usage

The bot supports the following commands:

- `/start`: Initiates the bot and prompts the user to share their location. Once the location is shared, the bot sends
  notifications to the user for flights in their area based on their preferences.

- `/stop`: Stops the user from receiving notifications.

- `/info`: Displays the current notification settings for the user.

- `/radius`: This command is used to set the radius for flight notifications. The radius is measured in meters. For
  example, `/radius 2000` sets the notification radius to 2000 meters. The default radius is 5000 meters.

- `/altitude`: Sets the altitude range for flight notifications. The altitude is measured in
  meters. The command can be used in two ways:

    - `/altitude <altitude>` sets the minimum and maximum altitude to the specified value.
    - `/altitude <min-altitude> <max-altitude>` sets the minimum and maximum altitude to the specified values.

  The default minimum altitude is 0 meters and the default maximum altitude is 100000 meters.

- `/altmin`: Shortcut for setting the minimum altitude. For example, `/altmin 1000` sets the minimum
  altitude to 1000 meters.

- `/altmax`: Shortcut for setting the maximum altitude. For example, `/altmax 10000` sets the maximum
  altitude to 10000 meters.

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

## Running the Script

To run the script, execute the following command:

```
python main.py
```