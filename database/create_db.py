from config import RAW_DATA_PATH
import sqlite3
import pandas as pd

from modules.cleaning import clean_data


# =========================
# 讀取CSV
# =========================

df = pd.read_csv(
    RAW_DATA_PATH
)


# =========================
# 清洗
# =========================

df = clean_data(df)


# =========================
# 連接正確資料庫
# =========================

conn = sqlite3.connect(
    "database/coffee_shop.db"
)


# =========================
# 建立資料表
# =========================

df.to_sql(
    "coffee_sales",
    conn,
    if_exists="replace",
    index=False
)


conn.close()

print("✅ 建立成功")
print("資料筆數:", len(df))
