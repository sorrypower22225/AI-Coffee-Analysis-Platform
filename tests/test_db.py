import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import RAW_DATA_PATH
import pandas as pd

from modules.cleaning import clean_data
from modules.db import save_to_db
from modules.db import load_data

# =========================
# 讀取 CSV
# =========================

df = pd.read_csv(
    RAW_DATA_PATH
)

# =========================
# 清洗
# =========================

df = clean_data(df)

# =========================
# 存入 SQLite
# =========================

save_to_db(df)

# =========================
# 重新讀取
# =========================

new_df = load_data()

print(new_df.head())
