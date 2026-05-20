import json
import os
import time
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


# =====================================================
# Real Historical Weather Service｜Open-Meteo
# 免費、免 API Key、可用於紐約歷史天氣
# =====================================================

NYC_LATITUDE = 40.7128
NYC_LONGITUDE = -74.0060
NYC_TIMEZONE = "America/New_York"

DAILY_WEATHER_FIELDS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "rain_sum",
    "snowfall_sum",
    "wind_speed_10m_max",
]


def _project_root():
    return Path(__file__).resolve().parents[1]


def _cache_dir():
    cache_path = _project_root() / "data" / "weather_cache"
    cache_path.mkdir(parents=True, exist_ok=True)
    return cache_path


def _cache_file(start_date, end_date):
    safe_start = str(start_date).replace("-", "")
    safe_end = str(end_date).replace("-", "")
    return _cache_dir() / f"nyc_open_meteo_{safe_start}_{safe_end}.csv"


def _build_open_meteo_url(start_date, end_date):
    params = {
        "latitude": NYC_LATITUDE,
        "longitude": NYC_LONGITUDE,
        "start_date": str(start_date),
        "end_date": str(end_date),
        "daily": ",".join(DAILY_WEATHER_FIELDS),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": NYC_TIMEZONE,
    }
    return "https://archive-api.open-meteo.com/v1/archive?" + urllib.parse.urlencode(params)


def fetch_open_meteo_daily_weather(start_date, end_date, force_refresh=False, timeout=6):
    """
    從 Open-Meteo 下載紐約每日歷史天氣。

    回傳欄位：
    - transaction_date
    - weather_temp_max_c
    - weather_temp_min_c
    - weather_temp_mean_c
    - weather_precipitation_mm
    - weather_rain_mm
    - weather_snowfall_mm
    - weather_wind_speed_max_kmh
    - weather_source
    - weather_is_real

    若 API 暫時失敗，會丟出例外，讓 features_service 使用代理天氣備援。
    """
    start_date = pd.to_datetime(start_date).date()
    end_date = pd.to_datetime(end_date).date()

    cache_file = _cache_file(start_date, end_date)
    if cache_file.exists() and not force_refresh:
        cached = pd.read_csv(cache_file)
        cached["transaction_date"] = pd.to_datetime(cached["transaction_date"])
        return cached

    url = _build_open_meteo_url(start_date, end_date)

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "AI-Coffee-Ultimate/1.0",
            "Accept": "application/json",
        },
    )

    last_error = None
    for attempt in range(1):
        try:
            with urllib.request.urlopen(req, timeout=timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
            break
        except Exception as exc:
            last_error = exc
            # 快速失敗，交給 features_service 使用月份代理天氣備援，避免 Streamlit 卡住。
            time.sleep(0.2)
    else:
        raise RuntimeError(f"Open-Meteo API 連線失敗：{last_error}")

    if "daily" not in payload or "time" not in payload["daily"]:
        raise RuntimeError(f"Open-Meteo 回傳格式異常：{payload}")

    daily = payload["daily"]
    weather_df = pd.DataFrame({"transaction_date": pd.to_datetime(daily["time"])})

    rename_map = {
        "temperature_2m_max": "weather_temp_max_c",
        "temperature_2m_min": "weather_temp_min_c",
        "temperature_2m_mean": "weather_temp_mean_c",
        "precipitation_sum": "weather_precipitation_mm",
        "rain_sum": "weather_rain_mm",
        "snowfall_sum": "weather_snowfall_mm",
        "wind_speed_10m_max": "weather_wind_speed_max_kmh",
    }

    for api_col, final_col in rename_map.items():
        values = daily.get(api_col, [])
        weather_df[final_col] = pd.to_numeric(pd.Series(values), errors="coerce")

    weather_df["weather_source"] = "Open-Meteo Historical Weather API"
    weather_df["weather_is_real"] = 1

    weather_df.to_csv(cache_file, index=False, encoding="utf-8-sig")
    return weather_df


def get_nyc_daily_weather_for_transactions(df, force_refresh=False):
    """
    根據交易資料日期，自動下載需要的紐約歷史天氣範圍。
    """
    if "transaction_date" not in df.columns:
        raise ValueError("缺少 transaction_date，無法抓取真實歷史天氣")

    dates = pd.to_datetime(df["transaction_date"], errors="coerce").dropna()
    if dates.empty:
        raise ValueError("transaction_date 無有效日期，無法抓取真實歷史天氣")

    start_date = dates.min().date()
    end_date = dates.max().date()

    return fetch_open_meteo_daily_weather(
        start_date=start_date,
        end_date=end_date,
        force_refresh=force_refresh,
    )
