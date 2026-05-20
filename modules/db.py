import pandas as pd

from database.connection import (
    get_connection
)

# =========================
# 存入 SQLite
# =========================

def save_to_db(df):

    conn = get_connection()

    df.to_sql(
        'coffee_sales',
        conn,
        if_exists='replace',
        index=False
    )

    conn.close()

    print(
        "✅ 資料成功存入 SQLite"
    )


# =========================
# 讀取 SQLite
# =========================

def load_data():

    conn = get_connection()

    query = """
    SELECT *
    FROM coffee_sales
    """

    df = pd.read_sql(
        query,
        conn
    )

    conn.close()

    return df