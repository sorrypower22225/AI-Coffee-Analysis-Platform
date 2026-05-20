import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.weather import (
    get_current_weather,
    get_historical_weather
)

# =========================
# 即時天氣
# =========================

current_weather = get_current_weather(
    'New York'
)

print("\n☕ 即時天氣\n")

print(current_weather)

# =========================
# 歷史天氣
# =========================

history_df = get_historical_weather()

print("\n☕ 2023 紐約歷史天氣\n")

print(history_df.head())

print(history_df.tail())