# ==========================================
# forecasting.py
# AI Forecasting Models
# ==========================================

import pandas as pd
import numpy as np

from prophet import Prophet

from sklearn.model_selection import train_test_split

from sklearn.linear_model import LinearRegression

from sklearn.ensemble import RandomForestRegressor

from xgboost import XGBRegressor

from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

# ==========================================
# 建立特徵
# ==========================================

def prepare_features(df):

    feature_df = df.copy()

    # 月份
    feature_df['Month'] = (
        feature_df['transaction_date']
        .dt.month
    )

    # 日期
    feature_df['Day'] = (
        feature_df['transaction_date']
        .dt.day
    )

    # 特徵欄位
    features = [
        'Hour',
        'Month',
        'Day',
        'transaction_qty',
        'unit_price'
    ]

    X = feature_df[features]

    y = feature_df['Total_Bill']

    # 切分資料
    X_train, X_test, y_train, y_test = (
        train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )
    )

    return (
        X_train,
        X_test,
        y_train,
        y_test
    )

# ==========================================
# 評估模型
# ==========================================

def evaluate_model(y_test, predictions):

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    return {
        'MAE': mae,
        'RMSE': rmse,
        'R2': r2
    }

# ==========================================
# Linear Regression
# ==========================================

def linear_regression_model(
    X_train,
    X_test,
    y_train,
    y_test
):

    model = LinearRegression()

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    metrics = evaluate_model(
        y_test,
        predictions
    )

    return model, metrics

# ==========================================
# Random Forest
# ==========================================

def random_forest_model(
    X_train,
    X_test,
    y_train,
    y_test
):

    model = RandomForestRegressor(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    metrics = evaluate_model(
        y_test,
        predictions
    )

    return model, metrics

# ==========================================
# XGBoost
# ==========================================

def xgboost_model(
    X_train,
    X_test,
    y_train,
    y_test
):

    model = XGBRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=6,
        random_state=42
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    metrics = evaluate_model(
        y_test,
        predictions
    )

    return model, metrics

# ==========================================
# Prophet Forecast
# ==========================================

def prophet_forecast(df):

    prophet_df = (
        df.groupby('transaction_date')
        ['Total_Bill']
        .sum()
        .reset_index()
    )

    prophet_df.columns = [
        'ds',
        'y'
    ]

    model = Prophet()

    model.fit(prophet_df)

    future = model.make_future_dataframe(
        periods=30
    )

    forecast = model.predict(
        future
    )

    return model, forecast