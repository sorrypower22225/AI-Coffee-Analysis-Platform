import os
import pandas as pd
import requests


STORE_LOCATIONS = {
    "Astoria": {
        "latitude": 40.7644,
        "longitude": -73.9235
    },
    "Hell's Kitchen": {
        "latitude": 40.7648,
        "longitude": -73.9927
    },
    "Lower Manhattan": {
        "latitude": 40.7075,
        "longitude": -74.0113
    }
}


def translate_weather_code(code):

    weather_map = {
        0: "晴天",
        1: "大致晴朗",
        2: "局部多雲",
        3: "陰天",
        45: "有霧",
        48: "霧凇",
        51: "小毛毛雨",
        53: "中度毛毛雨",
        55: "大毛毛雨",
        61: "小雨",
        63: "中雨",
        65: "大雨",
        71: "小雪",
        73: "中雪",
        75: "大雪",
        80: "陣雨",
        81: "中度陣雨",
        82: "強陣雨",
        95: "雷雨"
    }

    return weather_map.get(code, "未知天氣")


def generate_weather_insight(row):

    temperature = row["temperature"]
    humidity = row["humidity"]
    precipitation = row["precipitation"]
    weather_code = row["weather_code"]

    weather_text = translate_weather_code(weather_code)

    insights = []

    if temperature is not None and temperature <= 12:
        insights.append("今日氣溫偏低，建議增加熱咖啡、熱拿鐵與熱飲備貨。")

    if humidity is not None and humidity >= 70:
        insights.append("今日濕度偏高，可能影響來客舒適度與外帶需求。")

    if precipitation is not None and precipitation > 0:
        insights.append("目前有降雨，建議提高外送備貨與雨天熱飲供應。")

    if weather_code == 0:
        insights.append("今日天氣晴朗，可能提高冰飲、外帶與午後消費需求。")

    if temperature is not None and temperature >= 25:
        insights.append("今日氣溫偏高，建議增加冰飲、冷萃與清爽類商品備貨。")

    if not insights:
        insights.append("今日天氣穩定，可依照一般營運節奏備貨。")

    return " ".join(insights), weather_text


def get_store_coordinates(store_location):

    return STORE_LOCATIONS.get(store_location)


def _openweather_current_weather(store_location, coords, api_key):
    """OpenWeather 即時天氣。若沒有 API Key 或失敗，主流程會自動改用 Open-Meteo。"""
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "lat": coords["latitude"],
        "lon": coords["longitude"],
        "appid": api_key,
        "units": "metric",
        "lang": "zh_tw",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    main = data.get("main", {})
    weather = (data.get("weather") or [{}])[0]
    rain = data.get("rain", {}) or {}
    row = {
        "store_location": store_location,
        "temperature": main.get("temp"),
        "humidity": main.get("humidity"),
        "precipitation": rain.get("1h", 0),
        "weather_code": None,
        "天氣狀態": weather.get("description") or weather.get("main") or "未知天氣",
        "weather_source": "OpenWeather API",
    }
    # 讓共用洞察邏輯可運作
    insight, _ = generate_weather_insight({
        "temperature": row["temperature"],
        "humidity": row["humidity"],
        "precipitation": row["precipitation"],
        "weather_code": 61 if float(row["precipitation"] or 0) > 0 else 0,
    })
    row["AI天氣建議"] = insight
    return row


def _open_meteo_current_weather(store_location, coords):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "weather_code"
        ],
        "timezone": "America/New_York"
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data.get("current", {})
    weather_code = current.get("weather_code")
    row = {
        "store_location": store_location,
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "weather_code": weather_code,
        "weather_source": "Open-Meteo API"
    }
    insight, weather_text = generate_weather_insight(row)
    row["天氣狀態"] = weather_text
    row["AI天氣建議"] = insight
    return row


def get_current_weather(store_location):

    coords = get_store_coordinates(store_location)

    if coords is None:
        return None

    api_key = os.getenv("OPENWEATHER_API_KEY", "").strip()
    if api_key:
        try:
            return _openweather_current_weather(store_location, coords, api_key)
        except Exception:
            # OpenWeather 失敗時不讓 Dashboard 掛掉，改用免費免 Key 的 Open-Meteo。
            pass

    return _open_meteo_current_weather(store_location, coords)


def get_all_current_weather():

    weather_list = []

    for store in STORE_LOCATIONS.keys():

        try:
            weather = get_current_weather(store)

            if weather is not None:
                weather_list.append(weather)

        except Exception:
            weather_list.append({
                "store_location": store,
                "temperature": None,
                "humidity": None,
                "precipitation": None,
                "weather_code": None,
                "天氣狀態": "讀取失敗",
                "AI天氣建議": "即時天氣讀取失敗，請確認網路連線。"
            })

    return pd.DataFrame(weather_list)


def get_historical_weather(
    store_location,
    start_date,
    end_date
):

    coords = get_store_coordinates(store_location)

    if coords is None:
        return pd.DataFrame()

    url = "https://archive-api.open-meteo.com/v1/archive"

    params = {
        "latitude": coords["latitude"],
        "longitude": coords["longitude"],
        "start_date": start_date,
        "end_date": end_date,
        "daily": [
            "temperature_2m_mean",
            "precipitation_sum",
            "rain_sum",
            "weather_code"
        ],
        "timezone": "America/New_York"
    }

    response = requests.get(
        url,
        params=params,
        timeout=15
    )

    response.raise_for_status()

    data = response.json()
    daily = data.get("daily", {})

    weather_df = pd.DataFrame({
        "transaction_date": daily.get("time", []),
        "temperature_mean": daily.get("temperature_2m_mean", []),
        "precipitation_sum": daily.get("precipitation_sum", []),
        "rain_sum": daily.get("rain_sum", []),
        "weather_code": daily.get("weather_code", [])
    })

    weather_df["transaction_date"] = pd.to_datetime(
        weather_df["transaction_date"],
        errors="coerce"
    )

    weather_df["store_location"] = store_location

    return weather_df


def get_all_historical_weather(
    start_date,
    end_date
):

    all_weather = []

    for store in STORE_LOCATIONS.keys():

        try:
            weather_df = get_historical_weather(
                store,
                start_date,
                end_date
            )

            all_weather.append(weather_df)

        except Exception:
            pass

    if not all_weather:
        return pd.DataFrame()

    return pd.concat(
        all_weather,
        ignore_index=True
    )


def merge_sales_with_weather(df):

    df = df.copy()
    df.columns = df.columns.str.strip()

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"],
        errors="coerce"
    )

    start_date = df["transaction_date"].min().strftime("%Y-%m-%d")
    end_date = df["transaction_date"].max().strftime("%Y-%m-%d")

    weather_df = get_all_historical_weather(
        start_date,
        end_date
    )

    if weather_df.empty:
        return df

    merged_df = df.merge(
        weather_df,
        on=[
            "transaction_date",
            "store_location"
        ],
        how="left"
    )

    return merged_df