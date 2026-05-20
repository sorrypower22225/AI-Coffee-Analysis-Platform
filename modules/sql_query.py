import sqlite3
import pandas as pd

# =========================
# SQL 查詢
# =========================

def run_query(query):

    conn = sqlite3.connect(
        'coffee_shop.db'
    )

    df = pd.read_sql_query(
        query,
        conn
    )

    conn.close()

    return df