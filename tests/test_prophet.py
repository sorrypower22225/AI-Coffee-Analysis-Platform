import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import RAW_DATA_PATH
import pandas as pd

from modules.cleaning import clean_data

from modules.forecasting import prophet_forecast

# =========================
# 讀取資料
# =========================

df = pd.read_csv(
    RAW_DATA_PATH
)

# =========================
# 清洗資料
# =========================

df = clean_data(df)

# =========================
# Prophet 預測
# =========================

model, forecast = prophet_forecast(df)

# =========================
# 顯示預測
# =========================

print(
    forecast[
        ['ds', 'yhat']
    ].tail()
)
