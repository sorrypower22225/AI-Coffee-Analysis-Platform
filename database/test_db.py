import sqlite3

conn = sqlite3.connect(
    "database/coffee_shop.db"
)

cursor = conn.cursor()

cursor.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
)

print("資料表：")
print(cursor.fetchall())

cursor.execute(
    "SELECT COUNT(*) FROM coffee_sales"
)

print("資料筆數：")
print(cursor.fetchall())

conn.close()