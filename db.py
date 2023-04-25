import os
import logging
import time
from typing import Final, Any, Mapping, Sequence

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import MySQLConnection, CMySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

from user import User

load_dotenv()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

logger = logging.getLogger(__name__)

DB_HOST: Final = os.getenv('DB_HOST')
DB_PORT: Final = os.getenv('DB_PORT')
DB_USER: Final = os.getenv('DB_USER')
DB_PASSWORD: Final = os.getenv('DB_PASSWORD')
DB_DATABASE: Final = os.getenv('DB_DATABASE')


def get_database() -> PooledMySQLConnection | MySQLConnection | CMySQLConnection | None:
    max_retries = 5
    retry_delay = 10

    for i in range(max_retries):
        try:
            return mysql.connector.connect(
                host=DB_HOST,
                port=DB_PORT,
                user=DB_USER,
                password=DB_PASSWORD,
                database=DB_DATABASE
            )
        except Exception as e:
            logger.exception(e)
            logger.warning(f"Failed to connect to database. Retrying in {retry_delay} seconds...")

        time.sleep(retry_delay)

    return None


# Insert

def insert_user(user: User) -> bool:
    db = get_database()
    if db is None:
        return False

    insert_user_query = """
        INSERT INTO users
        (id, latitude, longitude, radius, min_altitude, max_altitude)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (
        user.id,
        user.latitude,
        user.longitude,
        user.radius,
        user.min_altitude,
        user.max_altitude
    )

    with db.cursor() as cursor:
        cursor.execute(insert_user_query, values)
        db.commit()
        db.close()
        return True


def insert_flight(user_id: int, flight_id: str) -> bool:
    db = get_database()
    if db is None:
        return False

    insert_flight_query = """
        INSERT INTO user_flights
        (user_id, flight_id, timestamp)
        VALUES (%s, %s, %s)
    """
    values = (
        user_id,
        flight_id,
        time.time()
    )

    with db.cursor() as cursor:
        cursor.execute(insert_flight_query, values)
        db.commit()
        db.close()
        return True


# Select

def select_user(user_id: int) -> Mapping[str, Any] | None:
    db = get_database()
    if db is None:
        return None

    select_user_query = """
        SELECT * FROM users
        WHERE id=%s
    """
    values = (
        user_id,
    )

    with db.cursor(buffered=True, dictionary=True) as cursor:
        cursor.execute(select_user_query, values)
        entry = cursor.fetchone()
        db.close()
        return entry


def select_users() -> Sequence[Any] | None:
    db = get_database()
    if db is None:
        return None

    select_users_query = """
        SELECT * FROM users
    """

    with db.cursor(buffered=True, dictionary=True) as cursor:
        cursor.execute(select_users_query)
        users = cursor.fetchall()
        db.close()
        return users


def select_flight(user_id: int, flight_id: str) -> Mapping[str, Any] | None:
    db = get_database()
    if db is None:
        return None

    select_flight_query = """
        SELECT * FROM user_flights
        WHERE user_id=%s AND flight_id=%s
    """
    values = (
        user_id,
        flight_id
    )

    with db.cursor(buffered=True, dictionary=True) as cursor:
        cursor.execute(select_flight_query, values)
        flight = cursor.fetchone()
        db.close()
        return flight


# Update

def update_user(user: User) -> bool:
    db = get_database()
    if db is None:
        return False

    update_user_query = """
        UPDATE users
        SET latitude=%s, longitude=%s, radius=%s, min_altitude=%s, max_altitude=%s
        WHERE id=%s
    """
    values = (
        user.latitude,
        user.longitude,
        user.radius,
        user.min_altitude,
        user.max_altitude,
        user.id
    )

    with db.cursor() as cursor:
        cursor.execute(update_user_query, values)
        db.commit()
        db.close()
        return True


# Delete

def delete_user(user_id: int) -> bool:
    db = get_database()
    if db is None:
        return False

    delete_user_query = """
        DELETE FROM users
        WHERE id=%s
    """
    values = (
        user_id,
    )

    with db.cursor() as cursor:
        cursor.execute(delete_user_query, values)
        db.commit()
        db.close()
        return True
