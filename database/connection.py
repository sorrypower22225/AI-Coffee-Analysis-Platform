import sqlite3


DB_PATH = "database/coffee_shop.db"


def get_connection():

    conn = sqlite3.connect(
        DB_PATH
    )

    return conn