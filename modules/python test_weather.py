import pandas as pd

# =========================
# AI 天氣營收分析
# =========================

def weather_sales_insights(weather):

    insights = []

    temp = float(weather['temp_C'])

    humidity = float(weather['humidity'])

    condition = weather['weather']

    # =========================
    # 高溫分析
    # =========================

    if temp >= 30:

        insights.append(
            "🥤 高溫天氣：建議增加冰飲與冷萃咖啡庫存"
        )

    elif temp <= 10:

        insights.append(
            "☕ 低溫天氣：建議增加熱拿鐵與熱美式促銷"
        )

    # =========================
    # 雨天分析
    # =========================

    if (
        'rain' in condition.lower()
        or
        'shower' in condition.lower()
    ):

        insights.append(
            "🌧 雨天：建議加強外送與線上優惠"
        )

    # =========================
    # 濕度分析
    # =========================

    if humidity >= 80:

        insights.append(
            "💧 高濕度：冰飲需求可能增加"
        )

    # =========================
    # 一般建議
    # =========================

    if len(insights) == 0:

        insights.append(
            "📈 天氣穩定：維持一般營運策略"
        )

    return insights