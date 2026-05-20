import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.weather import get_current_weather

from modules.weather_sales import (
    weather_sales_insights
)

# =========================
# 即時天氣
# =========================

weather = get_current_weather(
    'New York'
)

print("\n☀ 即時天氣\n")

print(weather)

# =========================
# AI 天氣營收分析
# =========================

insights = weather_sales_insights(
    weather
)

print("\n🤖 AI 天氣營運建議\n")

for insight in insights:

    print(insight)