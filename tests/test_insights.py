import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import RAW_DATA_PATH
import pandas as pd

from modules.cleaning import clean_data

from modules.insights import generate_insights

# =========================
# 讀取資料
# =========================

df = pd.read_csv(
    RAW_DATA_PATH
)

df = clean_data(df)

# =========================
# AI 商業分析
# =========================

insights = generate_insights(df)

# =========================
# 顯示 AI 洞察
# =========================

print("\n☕ AI 商業洞察\n")

for insight in insights:

    print(insight)
