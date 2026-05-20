from config import RAW_DATA_PATH
import pandas as pd
from sqlalchemy import create_engine

# 讀取 CSV
df = pd.read_csv(
    RAW_DATA_PATH
)

# 改成你的 MySQL 資訊
user="root"
password="123456"
host="localhost"
port="3306"
database="coffee_ai"

engine=create_engine(
    f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
)

df.to_sql(
    "coffee_sales",
    con=engine,
    if_exists="replace",
    index=False
)

print("成功上傳 MySQL")
