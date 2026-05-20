
import numpy as np
import pandas as pd
from services.cleaning_service import clean_data

try:
    import holidays
except Exception:
    holidays = None

try:
    from services.real_weather_service import get_nyc_daily_weather_for_transactions
except Exception:
    get_nyc_daily_weather_for_transactions = None

STORE_LOCATION_PROFILE = {
    "Astoria": {"location_type_code": 1, "commuter_score": 0.70, "tourist_score": 0.35, "office_score": 0.45},
    "Hell's Kitchen": {"location_type_code": 3, "commuter_score": 0.85, "tourist_score": 0.90, "office_score": 0.80},
    "Lower Manhattan": {"location_type_code": 2, "commuter_score": 0.95, "tourist_score": 0.65, "office_score": 0.95},
}

NYC_MONTHLY_WEATHER_PROXY = {
    1: (1.0, 0.33), 2: (3.0, 0.30), 3: (7.0, 0.36), 4: (13.0, 0.38),
    5: (18.0, 0.36), 6: (23.0, 0.34), 7: (26.0, 0.35), 8: (25.0, 0.34),
    9: (21.0, 0.31), 10: (15.0, 0.32), 11: (9.0, 0.34), 12: (4.0, 0.35),
}

CATEGORICAL_COLUMNS = [
    "store_location", "product_category", "product_type", "product_detail", "size", "Size"
]

FEATURE_GROUP_KEYWORDS = {
    "時間特徵": ["year", "quarter", "month", "week", "day", "weekday", "hour", "minute", "season", "holiday", "payday"],
    "週期 sin/cos": ["_sin", "_cos"],
    "多層 lag": ["lag_"],
    "多 rolling": ["rolling_", "ma_", "std_", "min_", "max_"],
    "店面聚合特徵": ["store_", "location_"],
    "商品聚合特徵": ["product_", "category_", "type_", "detail_"],
    "每店尖峰特徵": ["store_peak", "store_hour", "peak"],
    "商品熱門度": ["popularity", "frequency", "rank", "share"],
    "天氣特徵": ["weather", "rain", "temp", "snow", "wind", "comfort"],
    "交易數值": ["qty", "price", "amount"],
}


def _fill_numeric(series, default=0):
    return pd.to_numeric(series, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(default)


def _safe_div(a, b):
    a_num = pd.to_numeric(a, errors="coerce")
    if np.isscalar(b):
        b_num = np.nan if float(b) == 0 else float(b)
    else:
        b_num = pd.to_numeric(b, errors="coerce").replace(0, np.nan)
    result = a_num / b_num
    if hasattr(result, "replace"):
        return result.replace([np.inf, -np.inf], np.nan).fillna(0)
    return 0 if not np.isfinite(result) else result


def _add_datetime_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if df["transaction_time"].notna().any():
        df["hour"] = df["transaction_time"].dt.hour
        df["minute"] = df["transaction_time"].dt.minute
    else:
        df["hour"] = pd.to_numeric(df.get("Hour", 0), errors="coerce")
        df["minute"] = 0
    if "Hour" in df.columns:
        df["hour"] = df["hour"].fillna(pd.to_numeric(df["Hour"], errors="coerce"))
    df["hour"] = _fill_numeric(df["hour"], 0).clip(0, 23).astype(int)
    df["minute"] = _fill_numeric(df["minute"], 0).clip(0, 59).astype(int)

    dt = df["transaction_date"]
    df["year"] = dt.dt.year
    df["quarter"] = dt.dt.quarter
    df["month"] = dt.dt.month
    df["day"] = dt.dt.day
    df["weekday"] = dt.dt.weekday
    df["week_of_year"] = dt.dt.isocalendar().week.astype(int)
    df["day_of_year"] = dt.dt.dayofyear
    df["is_weekend"] = df["weekday"].isin([5, 6]).astype(int)
    df["is_month_start"] = dt.dt.is_month_start.astype(int)
    df["is_month_end"] = dt.dt.is_month_end.astype(int)
    df["is_mid_month"] = df["day"].between(13, 17).astype(int)

    # 週期特徵：讓模型理解 23 點接近 0 點、12 月接近 1 月
    for col, period in [("hour", 24), ("weekday", 7), ("month", 12), ("day_of_year", 365), ("minute", 60)]:
        df[f"{col}_sin"] = np.sin(2 * np.pi * df[col] / period)
        df[f"{col}_cos"] = np.cos(2 * np.pi * df[col] / period)

    df["is_morning_peak"] = df["hour"].between(7, 10).astype(int)
    df["is_lunch_peak"] = df["hour"].between(11, 13).astype(int)
    df["is_evening_peak"] = df["hour"].between(16, 19).astype(int)
    df["is_peak_hour"] = ((df["is_morning_peak"] + df["is_lunch_peak"] + df["is_evening_peak"]) > 0).astype(int)
    df["is_off_peak_hour"] = (df["is_peak_hour"] == 0).astype(int)
    return df


def _add_calendar_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    years = sorted(df["year"].dropna().astype(int).unique().tolist()) or [2023]
    if holidays is not None:
        holiday_dates = set(holidays.US(years=years).keys())
    else:
        holiday_dates = set()
        for y in years:
            holiday_dates.update(pd.to_datetime([
                f"{y}-01-01", f"{y}-01-16", f"{y}-02-20", f"{y}-05-29", f"{y}-06-19",
                f"{y}-07-04", f"{y}-09-04", f"{y}-10-09", f"{y}-11-10", f"{y}-11-23", f"{y}-12-25"
            ]).date)
    tx_date = df["transaction_date"].dt.date
    df["is_us_holiday"] = tx_date.isin(holiday_dates).astype(int)
    df["is_pre_holiday"] = (df["transaction_date"] + pd.Timedelta(days=1)).dt.date.isin(holiday_dates).astype(int)
    df["is_post_holiday"] = (df["transaction_date"] - pd.Timedelta(days=1)).dt.date.isin(holiday_dates).astype(int)
    df["is_payday_period"] = df["day"].isin([1, 2, 3, 15, 16, 30, 31]).astype(int)
    df["season_winter"] = df["month"].isin([12, 1, 2]).astype(int)
    df["season_spring"] = df["month"].isin([3, 4, 5]).astype(int)
    df["season_summer"] = df["month"].isin([6, 7, 8]).astype(int)
    df["season_fall"] = df["month"].isin([9, 10, 11]).astype(int)
    df["is_christmas_season"] = ((df["month"] == 12) & (df["day"] >= 15)).astype(int)
    df["is_black_friday_period"] = ((df["month"] == 11) & (df["day"].between(20, 30))).astype(int)
    return df


def _add_weather_features(df: pd.DataFrame, use_real_weather=True, force_refresh_weather=False) -> pd.DataFrame:
    df = df.copy()
    df = df.loc[:, ~df.columns.duplicated()].copy()
    used_real = False
    if use_real_weather and get_nyc_daily_weather_for_transactions is not None:
        try:
            weather_df = get_nyc_daily_weather_for_transactions(
                df[["transaction_date"]].copy(), force_refresh=force_refresh_weather
            )
            weather_df = weather_df.loc[:, ~weather_df.columns.duplicated()].copy()
            weather_df["transaction_date"] = pd.to_datetime(weather_df["transaction_date"], errors="coerce")
            # 只保留天氣服務欄位，避免和上傳的 Enterprise CSV 既有欄位重複後產生 _x/_y 或長度不一致。
            keep_cols = ["transaction_date"] + [c for c in weather_df.columns if c.startswith("weather_")]
            weather_df = weather_df[keep_cols].drop_duplicates(subset=["transaction_date"])
            existing_weather_cols = [c for c in df.columns if c.startswith("weather_")]
            df = df.drop(columns=existing_weather_cols, errors="ignore")
            df = df.merge(weather_df, on="transaction_date", how="left")
            used_real = True
        except Exception:
            used_real = False
    if not used_real:
        df["avg_temp_c"] = df["month"].map(lambda m: NYC_MONTHLY_WEATHER_PROXY.get(int(m), (15.0, 0.33))[0])
        df["rain_prob"] = df["month"].map(lambda m: NYC_MONTHLY_WEATHER_PROXY.get(int(m), (15.0, 0.33))[1])
        df["weather_temp_mean_c"] = df["avg_temp_c"]
        df["weather_temp_max_c"] = df["avg_temp_c"] + 4
        df["weather_temp_min_c"] = df["avg_temp_c"] - 4
        df["weather_precipitation_mm"] = df["rain_prob"] * 10
        df["weather_rain_mm"] = df["weather_precipitation_mm"]
        df["weather_snowfall_mm"] = 0
        df["weather_wind_speed_max_kmh"] = 15
        df["weather_is_real"] = 0
    else:
        df["weather_is_real"] = 1
        if "avg_temp_c" not in df.columns:
            df["avg_temp_c"] = _fill_numeric(df.get("weather_temp_mean_c", 15), 15)
        if "rain_prob" not in df.columns:
            precip = _fill_numeric(df.get("weather_precipitation_mm", 0), 0)
            df["rain_prob"] = (precip / 25).clip(0, 1)
    df["avg_temp_c"] = _fill_numeric(df.get("avg_temp_c", 15), 15)
    df["rain_prob"] = _fill_numeric(df.get("rain_prob", 0), 0)
    precip = _fill_numeric(df.get("weather_precipitation_mm", 0), 0)
    snow = _fill_numeric(df.get("weather_snowfall_mm", 0), 0)
    df["is_cold_weather"] = (df["avg_temp_c"] <= 8).astype(int)
    df["is_hot_weather"] = (df["avg_temp_c"] >= 24).astype(int)
    df["is_rainy_day"] = (precip > 0).astype(int)
    df["is_heavy_rain_day"] = (precip >= 10).astype(int)
    df["is_snow_day"] = (snow > 0).astype(int)
    df["comfort_temp_score"] = (1 - (np.abs(df["avg_temp_c"] - 18) / 25)).clip(0, 1)
    return df


def _add_store_product_base_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "store_location" in df.columns:
        df["location_type_code"] = df["store_location"].map(lambda x: STORE_LOCATION_PROFILE.get(str(x), {}).get("location_type_code", 0))
        df["location_commuter_score"] = df["store_location"].map(lambda x: STORE_LOCATION_PROFILE.get(str(x), {}).get("commuter_score", 0.5))
        df["location_tourist_score"] = df["store_location"].map(lambda x: STORE_LOCATION_PROFILE.get(str(x), {}).get("tourist_score", 0.5))
        df["location_office_score"] = df["store_location"].map(lambda x: STORE_LOCATION_PROFILE.get(str(x), {}).get("office_score", 0.5))

    for col in ["store_id", "store_location", "product_id", "product_category", "product_type", "product_detail", "size", "Size"]:
        if col in df.columns:
            df[col] = df[col].astype(str).fillna("Unknown")
            codes, _ = pd.factorize(df[col], sort=True)
            df[f"{col}_code"] = codes.astype(int)

    text = pd.Series("", index=df.index, dtype="object")
    for col in ["product_category", "product_type", "product_detail"]:
        if col in df.columns:
            text = text + " " + df[col].astype(str).str.lower()
    df["is_coffee_item"] = text.str.contains("coffee|espresso|latte|cappuccino|americano|brew", regex=True).astype(int)
    df["is_tea_item"] = text.str.contains("tea|chai", regex=True).astype(int)
    df["is_food_item"] = text.str.contains("bakery|scone|croissant|biscotti|cookie|food|sandwich", regex=True).astype(int)
    if "unit_price" in df.columns:
        price = _fill_numeric(df["unit_price"], 0)
        df["is_high_price_item"] = (price >= price.quantile(0.75)).astype(int)
        df["price_level"] = pd.qcut(price.rank(method="first"), q=4, labels=False, duplicates="drop").fillna(0).astype(int)
    return df


def _add_business_aggregation_features(df: pd.DataFrame) -> pd.DataFrame:
    """店面聚合、商品聚合、商品熱門度、每店尖峰特徵。"""
    df = df.copy()
    amount = _fill_numeric(df["total_amount"], 0)
    qty = _fill_numeric(df.get("transaction_qty", 1), 1)
    df["item_revenue_per_qty"] = _safe_div(amount, qty)

    group_specs = []
    if "store_location" in df.columns:
        group_specs += [("store_location", "store"), (["store_location", "hour"], "store_hour"), (["store_location", "weekday"], "store_weekday")]
    elif "store_id" in df.columns:
        group_specs += [("store_id", "store"), (["store_id", "hour"], "store_hour"), (["store_id", "weekday"], "store_weekday")]
    if "product_category" in df.columns:
        group_specs += [("product_category", "product_category")]
    if "product_type" in df.columns:
        group_specs += [("product_type", "product_type")]
    if "product_detail" in df.columns:
        group_specs += [("product_detail", "product_detail")]
    if {"store_location", "product_category"}.issubset(df.columns):
        group_specs += [(["store_location", "product_category"], "store_category")]
    if {"store_location", "product_type"}.issubset(df.columns):
        group_specs += [(["store_location", "product_type"], "store_product_type")]

    for keys, prefix in group_specs:
        grouped = df.groupby(keys)["total_amount"]
        df[f"{prefix}_avg_sales"] = grouped.transform("mean")
        df[f"{prefix}_median_sales"] = grouped.transform("median")
        df[f"{prefix}_sales_std"] = grouped.transform("std").fillna(0)
        df[f"{prefix}_sales_count"] = grouped.transform("count")
        df[f"{prefix}_sales_share"] = _safe_div(grouped.transform("sum"), df["total_amount"].sum())
        if "transaction_qty" in df.columns:
            qg = df.groupby(keys)["transaction_qty"]
            df[f"{prefix}_avg_qty"] = qg.transform("mean")
            df[f"{prefix}_qty_sum"] = qg.transform("sum")

    # 每店尖峰特徵
    store_key = "store_location" if "store_location" in df.columns else ("store_id" if "store_id" in df.columns else None)
    if store_key is not None:
        peak_amount = df["total_amount"].where(df["is_peak_hour"] == 1, 0)
        off_amount = df["total_amount"].where(df["is_peak_hour"] == 0, 0)
        df["store_peak_sales_avg"] = peak_amount.groupby(df[store_key]).transform("mean")
        df["store_offpeak_sales_avg"] = off_amount.groupby(df[store_key]).transform("mean")
        df["store_peak_sales_ratio"] = _safe_div(df["store_peak_sales_avg"], df["store_offpeak_sales_avg"] + 1e-6)
        df["store_peak_transaction_count"] = df["is_peak_hour"].groupby(df[store_key]).transform("sum")

    # 商品熱門度
    for key, prefix in [("product_detail", "product"), ("product_type", "product_type"), ("product_category", "category")]:
        if key in df.columns:
            freq = df.groupby(key)[key].transform("count")
            total = max(len(df), 1)
            df[f"{prefix}_frequency"] = freq
            df[f"{prefix}_popularity"] = freq / total
            df[f"{prefix}_revenue_rank"] = df.groupby(key)["total_amount"].transform("sum").rank(method="dense", ascending=False)
            df[f"{prefix}_qty_rank"] = df.groupby(key)["transaction_qty"].transform("sum").rank(method="dense", ascending=False) if "transaction_qty" in df.columns else 0
    return df


def _add_lag_rolling_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    sort_key = [c for c in ["store_id", "store_location", "transaction_date", "hour"] if c in df.columns]
    if sort_key:
        df = df.sort_values(sort_key)
    store_key = "store_location" if "store_location" in df.columns else ("store_id" if "store_id" in df.columns else None)
    group_cols = ([store_key, "transaction_date"] if store_key else ["transaction_date"])
    daily = df.groupby(group_cols, as_index=False)["total_amount"].sum().rename(columns={"total_amount": "store_daily_sales"})
    daily = daily.sort_values(group_cols)
    target_group = daily.groupby(store_key)["store_daily_sales"] if store_key else daily["store_daily_sales"]
    for lag in [1, 2, 3, 7, 14, 30]:
        daily[f"store_daily_sales_lag_{lag}"] = target_group.shift(lag) if store_key else daily["store_daily_sales"].shift(lag)
    for win in [3, 7, 14, 30]:
        if store_key:
            shifted = daily.groupby(store_key)["store_daily_sales"].shift(1)
            daily[f"store_daily_sales_rolling_mean_{win}"] = shifted.groupby(daily[store_key]).transform(lambda s: s.rolling(win, min_periods=1).mean())
            daily[f"store_daily_sales_rolling_std_{win}"] = shifted.groupby(daily[store_key]).transform(lambda s: s.rolling(win, min_periods=2).std())
            daily[f"store_daily_sales_rolling_min_{win}"] = shifted.groupby(daily[store_key]).transform(lambda s: s.rolling(win, min_periods=1).min())
            daily[f"store_daily_sales_rolling_max_{win}"] = shifted.groupby(daily[store_key]).transform(lambda s: s.rolling(win, min_periods=1).max())
        else:
            shifted = daily["store_daily_sales"].shift(1)
            daily[f"store_daily_sales_rolling_mean_{win}"] = shifted.rolling(win, min_periods=1).mean()
            daily[f"store_daily_sales_rolling_std_{win}"] = shifted.rolling(win, min_periods=2).std()
            daily[f"store_daily_sales_rolling_min_{win}"] = shifted.rolling(win, min_periods=1).min()
            daily[f"store_daily_sales_rolling_max_{win}"] = shifted.rolling(win, min_periods=1).max()
    feature_cols = [c for c in daily.columns if c not in group_cols + ["store_daily_sales"]]
    df = df.merge(daily[group_cols + feature_cols], on=group_cols, how="left")

    # 每小時交易序列 lag/rolling
    hourly_group_cols = ([store_key, "transaction_date", "hour"] if store_key else ["transaction_date", "hour"])
    hourly = df.groupby(hourly_group_cols, as_index=False)["total_amount"].sum().rename(columns={"total_amount": "store_hourly_sales"})
    hourly = hourly.sort_values(hourly_group_cols)
    if store_key:
        hg = hourly.groupby(store_key)["store_hourly_sales"]
        for lag in [1, 2, 3, 6, 12, 24]:
            hourly[f"store_hourly_sales_lag_{lag}"] = hg.shift(lag)
        for win in [3, 6, 12, 24]:
            shifted = hourly.groupby(store_key)["store_hourly_sales"].shift(1)
            hourly[f"store_hourly_sales_rolling_mean_{win}"] = shifted.groupby(hourly[store_key]).transform(lambda s: s.rolling(win, min_periods=1).mean())
    else:
        for lag in [1, 2, 3, 6, 12, 24]:
            hourly[f"store_hourly_sales_lag_{lag}"] = hourly["store_hourly_sales"].shift(lag)
        for win in [3, 6, 12, 24]:
            hourly[f"store_hourly_sales_rolling_mean_{win}"] = hourly["store_hourly_sales"].shift(1).rolling(win, min_periods=1).mean()
    hcols = [c for c in hourly.columns if c not in hourly_group_cols + ["store_hourly_sales"]]
    df = df.merge(hourly[hourly_group_cols + hcols], on=hourly_group_cols, how="left")
    numeric_cols = df.select_dtypes(include=[np.number, "bool"]).columns
    df[numeric_cols] = df[numeric_cols].replace([np.inf, -np.inf], np.nan).fillna(df[numeric_cols].median(numeric_only=True)).fillna(0)
    return df


def generate_features(
    df: pd.DataFrame,
    use_official_holiday=True,
    add_lag_features=True,
    use_real_weather=True,
    force_refresh_weather=False,
    add_business_aggregates=True,
) -> pd.DataFrame:
    """Enterprise Feature Engine v2：65+特徵、店面/商品聚合、多層 lag/rolling、週期 sin/cos、每店尖峰、熱門度。"""
    df = clean_data(df)
    df = _add_datetime_features(df)
    df = _add_calendar_features(df)
    df = _add_weather_features(df, use_real_weather=use_real_weather, force_refresh_weather=force_refresh_weather)
    df = _add_store_product_base_features(df)
    if add_business_aggregates:
        df = _add_business_aggregation_features(df)
    if add_lag_features:
        df = _add_lag_rolling_features(df)
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    numeric_cols = df.select_dtypes(include=[np.number, "bool"]).columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    return df.reset_index(drop=True)


def build_features(df: pd.DataFrame, **kwargs) -> pd.DataFrame:
    return generate_features(df, **kwargs)


def classify_feature_group(feature_name: str) -> str:
    f = str(feature_name).lower()
    for group, keywords in FEATURE_GROUP_KEYWORDS.items():
        if any(k in f for k in keywords):
            return group
    return "其他特徵"


def build_feature_catalog(feature_names):
    rows = []
    for i, name in enumerate(feature_names, start=1):
        rows.append({"序號": i, "特徵": name, "特徵類型": classify_feature_group(name), "已使用": "✅"})
    return pd.DataFrame(rows)
