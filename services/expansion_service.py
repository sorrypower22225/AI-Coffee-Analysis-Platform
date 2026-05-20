import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

from services.cleaning_service import clean_data

CANDIDATE_LOCATIONS = pd.DataFrame([
    {
        "第四家店候選區域": "Midtown East",
        "定位": "辦公商圈 + 通勤客",
        "office_score": 0.95,
        "tourist_score": 0.65,
        "commuter_score": 0.92,
        "rent_risk": 0.82,
        "competition_risk": 0.72,
    },
    {
        "第四家店候選區域": "Williamsburg",
        "定位": "年輕族群 + 週末休閒",
        "office_score": 0.55,
        "tourist_score": 0.72,
        "commuter_score": 0.70,
        "rent_risk": 0.66,
        "competition_risk": 0.62,
    },
    {
        "第四家店候選區域": "Upper West Side",
        "定位": "住宅區 + 穩定回購",
        "office_score": 0.45,
        "tourist_score": 0.60,
        "commuter_score": 0.58,
        "rent_risk": 0.58,
        "competition_risk": 0.50,
    },
    {
        "第四家店候選區域": "Financial District East",
        "定位": "金融辦公 + 早餐午餐尖峰",
        "office_score": 0.98,
        "tourist_score": 0.55,
        "commuter_score": 0.96,
        "rent_risk": 0.88,
        "competition_risk": 0.78,
    },
])


def _scale(series):
    s = pd.to_numeric(series, errors="coerce").fillna(0)
    if s.nunique() <= 1:
        return pd.Series([0.7] * len(s), index=s.index)
    return pd.Series(MinMaxScaler().fit_transform(s.to_frame()).ravel(), index=s.index)


def calculate_store_scores(df):
    df = clean_data(df)
    result = df.groupby("store_location").agg(
        Total_Bill=("total_amount", "sum"),
        transaction_qty=("transaction_qty", "sum"),
        orders=("total_amount", "count"),
        avg_ticket=("total_amount", "mean"),
        active_days=("transaction_date", "nunique"),
    ).reset_index()
    result["daily_avg_sales"] = result["Total_Bill"] / result["active_days"].replace(0, np.nan)
    result["營收分數"] = _scale(result["Total_Bill"])
    result["銷量分數"] = _scale(result["transaction_qty"])
    result["客單分數"] = _scale(result["avg_ticket"])
    result["穩定分數"] = _scale(result["daily_avg_sales"])
    result["商圈分數"] = (
        result["營收分數"] * 0.45 +
        result["銷量分數"] * 0.25 +
        result["客單分數"] * 0.15 +
        result["穩定分數"] * 0.15
    )
    return result.sort_values("商圈分數", ascending=False).reset_index(drop=True)


def calculate_store_hour_product_profile(df):
    df = clean_data(df)
    df["hour"] = df["transaction_time"].dt.hour.fillna(df.get("Hour", 0)).astype(int)
    hourly = df.groupby(["store_location", "hour"], as_index=False)["total_amount"].sum()
    peak = hourly.loc[hourly.groupby("store_location")["total_amount"].idxmax()].rename(columns={"hour": "尖峰小時", "total_amount": "尖峰小時營收"})
    top_cat = df.groupby(["store_location", "product_category"], as_index=False)["total_amount"].sum()
    top_cat = top_cat.loc[top_cat.groupby("store_location")["total_amount"].idxmax()].rename(columns={"product_category": "主力商品類別", "total_amount": "主力商品營收"})
    return peak.merge(top_cat, on="store_location", how="left")


def predict_fourth_store_candidates(df):
    score = calculate_store_scores(df)
    avg_daily_sales = score["daily_avg_sales"].mean()
    avg_ticket = score["avg_ticket"].mean()
    best_store_score = score["商圈分數"].max()

    candidates = CANDIDATE_LOCATIONS.copy()
    candidates["需求分數"] = (
        candidates["office_score"] * 0.40 +
        candidates["commuter_score"] * 0.35 +
        candidates["tourist_score"] * 0.25
    )
    candidates["風險扣分"] = (
        candidates["rent_risk"] * 0.55 +
        candidates["competition_risk"] * 0.45
    )
    candidates["第四家店成功率"] = (
        0.50 + candidates["需求分數"] * 0.38 + best_store_score * 0.22 - candidates["風險扣分"] * 0.20
    ).clip(0, 0.95)
    candidates["預估每日營收"] = avg_daily_sales * (0.85 + candidates["需求分數"] * 0.45 - candidates["rent_risk"] * 0.12)
    candidates["預估月營收"] = candidates["預估每日營收"] * 30
    candidates["預估客單價"] = avg_ticket * (0.95 + candidates["office_score"] * 0.08 + candidates["tourist_score"] * 0.04)
    candidates["展店總分"] = (
        candidates["第四家店成功率"] * 100 * 0.55 +
        _scale(candidates["預估月營收"]) * 100 * 0.30 +
        (1 - candidates["風險扣分"]) * 100 * 0.15
    )
    return candidates.sort_values("展店總分", ascending=False).reset_index(drop=True)


def expansion_ai_model(df):
    score = calculate_store_scores(df)
    profile = calculate_store_hour_product_profile(df)
    candidates = predict_fourth_store_candidates(df)
    best = score.iloc[0]
    fourth = candidates.iloc[0]
    profile_best = profile[profile["store_location"] == best["store_location"]]
    if not profile_best.empty:
        p = profile_best.iloc[0]
        peak_text = f"尖峰小時 {int(p['尖峰小時'])}:00，主力商品類別：{p['主力商品類別']}"
    else:
        peak_text = "尖峰與商品資料不足"

    return f"""
### ✅ 三家店分析結論

目前三家店中，表現最佳的是 **{best['store_location']}**。

- 商圈分數：{best['商圈分數']:.2f}
- 總營收：${best['Total_Bill']:,.0f}
- 平均客單價：${best['avg_ticket']:.2f}
- {peak_text}

### 🏪 第四家店建議

建議優先評估：**{fourth['第四家店候選區域']}**

- 定位：{fourth['定位']}
- 預估每日營收：${fourth['預估每日營收']:,.0f}
- 預估月營收：${fourth['預估月營收']:,.0f}
- 預估成功率：{fourth['第四家店成功率']*100:.1f}%
- 展店總分：{fourth['展店總分']:.1f}

### 📌 商業建議

1. 第四家店應複製最佳門市的尖峰人力配置與主力商品策略。  
2. 開幕前 30 天主打高人氣商品與早餐/午餐尖峰套餐。  
3. 若租金壓力過高，優先選擇展店總分第二名作為保守方案。  
"""
