import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import RAW_DATA_PATH
import pandas as pd

from sklearn.model_selection import train_test_split

from modules.cleaning import clean_data

from modules.forecasting import (
    prepare_features,
    linear_regression_model,
    random_forest_model,
    xgboost_model
)

# =========================
# 讀取資料
# =========================

df = pd.read_csv(
    RAW_DATA_PATH
)

df = clean_data(df)

# =========================
# 建立特徵
# =========================

X, y = prepare_features(df)

# =========================
# 切分資料
# =========================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# =========================
# Linear Regression
# =========================

_, lr_metrics = linear_regression_model(
    X_train,
    X_test,
    y_train,
    y_test
)

# =========================
# Random Forest
# =========================

_, rf_metrics = random_forest_model(
    X_train,
    X_test,
    y_train,
    y_test
)

# =========================
# XGBoost
# =========================

_, xgb_metrics = xgboost_model(
    X_train,
    X_test,
    y_train,
    y_test
)

# =========================
# 顯示結果
# =========================

print("\n📈 Linear Regression")
print(lr_metrics)

print("\n🌲 Random Forest")
print(rf_metrics)

print("\n🚀 XGBoost")
print(xgb_metrics)
