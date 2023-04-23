import os
import logging
import time
from typing import Final, Any, Mapping, Sequence

import mysql.connector
from dotenv import load_dotenv
from mysql.connector import MySQLConnection, CMySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

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


# Update


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
