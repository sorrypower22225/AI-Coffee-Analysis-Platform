import os
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "Coffee_Shop_Enterprise_Features_Corrected.csv")
OUTPUT_FILE = os.path.join(BASE_DIR, "data", "Coffee_Shop_PowerBI_Dashboard_Data.csv")

if not os.path.exists(INPUT_FILE):
    raise FileNotFoundError(
        f"找不到完整版清洗資料：{INPUT_FILE}\n"
        "請把 Coffee_Shop_Enterprise_Features_Corrected.csv 放到 data 資料夾後再執行。"
    )

all_columns = pd.read_csv(INPUT_FILE, nrows=0).columns.tolist()
keep_columns = [
    "transaction_id", "transaction_date", "transaction_time",
    "store_id", "store_location", "product_id",
    "product_category", "product_type", "product_detail", "size",
    "transaction_qty", "unit_price", "total_amount", "Total_Bill", "total_bill",
    "month_name", "day_name", "hour", "Hour", "month", "Month", "day", "Day",
    "weekday", "day_of_week", "Day of Week", "is_weekend",
    "is_peak_hour", "is_off_peak_hour", "is_morning_peak", "is_lunch_peak", "is_evening_peak",
    "weather_temp_max_c", "weather_temp_min_c", "weather_temp_mean_c",
    "weather_precipitation_mm", "weather_rain_mm", "weather_is_real",
    "is_rainy_day", "is_heavy_rain_day", "avg_temp_c", "rain_prob"
]
available_columns = [c for c in keep_columns if c in all_columns]
df = pd.read_csv(INPUT_FILE, usecols=available_columns)

df = df.rename(columns={
    "Total_Bill": "total_bill_original",
    "total_bill": "total_bill_lower",
    "Hour": "hour_original",
    "Month": "month_original",
    "Day": "day_original",
    "Day of Week": "day_of_week_original",
    "day_of_week": "day_of_week_num",
})

if "total_amount" not in df.columns:
    if "total_bill_original" in df.columns:
        df["total_amount"] = df["total_bill_original"]
    elif "total_bill_lower" in df.columns:
        df["total_amount"] = df["total_bill_lower"]
    else:
        df["total_amount"] = df["transaction_qty"] * df["unit_price"]

if "hour" not in df.columns and "hour_original" in df.columns:
    df["hour"] = df["hour_original"]
if "month" not in df.columns and "month_original" in df.columns:
    df["month"] = df["month_original"]
if "day" not in df.columns and "day_original" in df.columns:
    df["day"] = df["day_original"]

if "transaction_date" in df.columns:
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df["year"] = df["transaction_date"].dt.year
    df["quarter"] = "Q" + df["transaction_date"].dt.quarter.astype("Int64").astype(str)
    if "day_name" not in df.columns:
        df["day_name"] = df["transaction_date"].dt.day_name()
    if "month_name" not in df.columns:
        df["month_name"] = df["transaction_date"].dt.month_name()

if "is_peak_hour" not in df.columns and "hour" in df.columns:
    df["is_peak_hour"] = df["hour"].apply(lambda x: 1 if x in [8, 9, 10, 11, 12, 13, 17, 18] else 0)
if "is_peak_hour" in df.columns:
    df["peak_status"] = df["is_peak_hour"].apply(lambda x: "尖峰" if int(x) == 1 else "離峰")

if "is_rainy_day" not in df.columns:
    if "weather_rain_mm" in df.columns:
        df["is_rainy_day"] = (df["weather_rain_mm"].fillna(0) > 0).astype(int)
    elif "weather_precipitation_mm" in df.columns:
        df["is_rainy_day"] = (df["weather_precipitation_mm"].fillna(0) > 0).astype(int)

if "is_rainy_day" in df.columns:
    df["weather_status"] = df["is_rainy_day"].apply(lambda x: "雨天" if int(x) == 1 else "非雨天")

front_columns = [
    "transaction_id", "transaction_date", "transaction_time",
    "store_id", "store_location", "product_id",
    "product_category", "product_type", "product_detail", "size",
    "transaction_qty", "unit_price", "total_amount",
    "month_name", "day_name", "year", "quarter", "month", "day", "weekday", "day_of_week_num", "hour",
    "is_weekend", "is_peak_hour", "peak_status", "is_morning_peak", "is_lunch_peak", "is_evening_peak", "is_off_peak_hour",
    "weather_status", "weather_temp_max_c", "weather_temp_min_c", "weather_temp_mean_c",
    "weather_precipitation_mm", "weather_rain_mm", "avg_temp_c", "rain_prob",
    "is_rainy_day", "is_heavy_rain_day", "weather_is_real"
]
ordered_columns = [c for c in front_columns if c in df.columns] + [c for c in df.columns if c not in front_columns]
df = df[ordered_columns]

df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
print("✅ Power BI 專用資料已建立：", OUTPUT_FILE)
print("筆數：", len(df))
print("欄位數：", len(df.columns))
