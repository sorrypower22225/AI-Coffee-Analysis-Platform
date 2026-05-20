from config import RAW_DATA_PATH
import sqlite3
import pandas as pd


conn = sqlite3.connect(
    "database/coffee_shop.db"
)


df = pd.read_csv(
    RAW_DATA_PATH
)


print(df.head())

print(
    "CSV總筆數:",
    len(df)
)


df.to_sql(

    "coffee_sales",

    conn,

    if_exists="replace",

    index=False

)

conn.close()

print(
    "coffee_sales 資料表建立成功"
)
