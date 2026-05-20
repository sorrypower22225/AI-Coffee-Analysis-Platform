import os
import sys

import pandas as pd
import plotly.express as px
import streamlit as st


# 讓此頁可直接被 app.py 安全載入
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from services.features_service import generate_features
from services.weather_service import get_all_current_weather
from utils.shared_data import get_shared_raw_data
from utils.data_loader import load_default_data, read_csv_safely
from utils.schema import ensure_required_columns


@st.cache_data(show_spinner=False)
def load_default_sales_data():
    df = load_default_data(prefer_feature=True)
    return df if df is not None else pd.DataFrame()


def _load_sales_data(uploaded_file=None):
    if uploaded_file is not None:
        return read_csv_safely(uploaded_file)

    df, _source_name = get_shared_raw_data(prefer_feature=True)
    if df is not None:
        return df

    return load_default_sales_data()


def _safe_currency(value):
    """安全顯示金額，避免畫面出現 $nan / $inf。"""
    try:
        numeric_value = pd.to_numeric(value, errors="coerce")
        if pd.isna(numeric_value):
            return "無資料"
        if numeric_value == float("inf") or numeric_value == float("-inf"):
            return "無資料"
        return f"${float(numeric_value):,.0f}"
    except Exception:
        return "無資料"


def _prepare_weather_dataset(df, use_real_weather, force_refresh_weather):
    df = ensure_required_columns(df)
    feature_df = generate_features(
        df,
        use_official_holiday=True,
        add_lag_features=True,
        use_real_weather=use_real_weather,
        force_refresh_weather=force_refresh_weather,
    )

    if "transaction_date" in feature_df.columns:
        feature_df["transaction_date"] = pd.to_datetime(
            feature_df["transaction_date"],
            errors="coerce"
        )

    return feature_df


def _daily_weather_summary(feature_df):
    feature_df = ensure_required_columns(feature_df)
    group_cols = ["transaction_date"]
    if "store_location" in feature_df.columns:
        group_cols.append("store_location")

    agg_map = {
        "Total_Bill": "sum",
        "transaction_qty": "sum",
        "avg_temp_c": "mean",
        "weather_precipitation_mm": "mean",
        "is_rainy_day": "max",
        "is_hot_weather": "max",
        "is_cold_weather": "max",
        "is_peak_hour": "mean",
    }

    available_agg = {
        col: func
        for col, func in agg_map.items()
        if col in feature_df.columns
    }

    daily = (
        feature_df
        .groupby(group_cols, dropna=False)
        .agg(available_agg)
        .reset_index()
    )

    rename_map = {
        "Total_Bill": "每日營收",
        "transaction_qty": "每日銷量",
        "avg_temp_c": "平均氣溫°C",
        "weather_precipitation_mm": "降雨量mm",
        "is_rainy_day": "是否下雨",
        "is_hot_weather": "是否高溫",
        "is_cold_weather": "是否低溫",
        "is_peak_hour": "尖峰時段占比",
    }

    return daily.rename(columns=rename_map)


def _category_weather_summary(feature_df):
    if "product_category" not in feature_df.columns:
        return pd.DataFrame()

    weather_label = pd.Series("一般天氣", index=feature_df.index)
    if "is_rainy_day" in feature_df.columns:
        weather_label = weather_label.mask(feature_df["is_rainy_day"] == 1, "下雨天")
    if "is_hot_weather" in feature_df.columns:
        weather_label = weather_label.mask(feature_df["is_hot_weather"] == 1, "高溫天")
    if "is_cold_weather" in feature_df.columns:
        weather_label = weather_label.mask(feature_df["is_cold_weather"] == 1, "低溫天")

    temp_df = feature_df.copy()
    temp_df["天氣類型"] = weather_label

    value_col = "Total_Bill" if "Total_Bill" in temp_df.columns else None
    qty_col = "transaction_qty" if "transaction_qty" in temp_df.columns else None

    agg = {}
    if value_col:
        agg[value_col] = "sum"
    if qty_col:
        agg[qty_col] = "sum"

    if not agg:
        return pd.DataFrame()

    result = (
        temp_df
        .groupby(["天氣類型", "product_category"], dropna=False)
        .agg(agg)
        .reset_index()
        .rename(columns={
            "product_category": "商品類別",
            "Total_Bill": "營收",
            "transaction_qty": "銷量",
        })
    )

    return result


def run_weather_analysis_page():
    st.title("🌦️ 天氣 × 營收影響分析")
    st.caption("整合 Open-Meteo 歷史天氣、降雨、氣溫、尖峰時段、來客量代理與銷售預測特徵。")

    st.info("本頁會優先使用左側全平台共用 CSV；若未上傳，會使用內建原始資料。")

    use_real_weather = st.checkbox(
        "使用 Open-Meteo 真實歷史天氣 API（失敗會自動使用代理天氣）",
        value=True
    )
    force_refresh_weather = st.checkbox(
        "重新下載天氣快取",
        value=False
    )

    try:
        df, source_name = get_shared_raw_data(prefer_feature=False)
    except Exception as exc:
        st.error("❌ 資料讀取失敗")
        st.code(str(exc))
        return

    if df is None or df.empty:
        st.warning("找不到銷售資料，請先在左側上傳 CSV。")
        return

    st.success(f"✅ 已載入資料：{source_name}")

    with st.spinner("正在整合天氣與銷售資料..."):
        try:
            feature_df = _prepare_weather_dataset(
                df,
                use_real_weather=use_real_weather,
                force_refresh_weather=force_refresh_weather,
            )
        except Exception as exc:
            st.error("❌ 天氣特徵整合失敗")
            st.code(str(exc))
            return

    weather_source = "未知"
    if "weather_source" in feature_df.columns:
        weather_source = str(feature_df["weather_source"].dropna().iloc[0]) if not feature_df["weather_source"].dropna().empty else "未知"

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("資料筆數", f"{len(feature_df):,}")
    c2.metric("天氣來源", weather_source)
    c3.metric("下雨交易占比", f"{feature_df.get('is_rainy_day', pd.Series([0])).mean() * 100:.1f}%")
    c4.metric("平均氣溫", f"{feature_df.get('avg_temp_c', pd.Series([0])).mean():.1f}°C")

    if "weather_api_error" in feature_df.columns:
        error_text = str(feature_df["weather_api_error"].dropna().iloc[0]) if not feature_df["weather_api_error"].dropna().empty else ""
        if error_text:
            st.warning(f"Open-Meteo 連線失敗，已自動改用代理天氣。原因：{error_text}")

    st.markdown("---")
    st.subheader("📌 天氣對營收的核心指標")

    daily = _daily_weather_summary(feature_df)

    if not daily.empty and "每日營收" in daily.columns:
        # 若固定高溫/低溫門檻沒有命中資料，改用資料分位數做「相對高溫 / 相對低溫」判斷，避免指標顯示 $nan。
        temp_note = ""
        if "平均氣溫°C" in daily.columns:
            temp_series = pd.to_numeric(daily["平均氣溫°C"], errors="coerce")

            if "是否高溫" not in daily.columns or pd.to_numeric(daily.get("是否高溫", 0), errors="coerce").fillna(0).sum() == 0:
                high_threshold = temp_series.quantile(0.75)
                if pd.notna(high_threshold):
                    daily["是否高溫"] = (temp_series >= high_threshold).astype(int)
                    temp_note = "高溫天採用資料前 25% 較高氣溫日判定。"

            if "是否低溫" not in daily.columns or pd.to_numeric(daily.get("是否低溫", 0), errors="coerce").fillna(0).sum() == 0:
                low_threshold = temp_series.quantile(0.25)
                if pd.notna(low_threshold):
                    daily["是否低溫"] = (temp_series <= low_threshold).astype(int)

        rainy_revenue = daily.loc[pd.to_numeric(daily.get("是否下雨", 0), errors="coerce").fillna(0) == 1, "每日營收"].mean()
        normal_revenue = daily.loc[pd.to_numeric(daily.get("是否下雨", 0), errors="coerce").fillna(0) == 0, "每日營收"].mean()
        hot_revenue = daily.loc[pd.to_numeric(daily.get("是否高溫", 0), errors="coerce").fillna(0) == 1, "每日營收"].mean()
        cold_revenue = daily.loc[pd.to_numeric(daily.get("是否低溫", 0), errors="coerce").fillna(0) == 1, "每日營收"].mean()

        k1, k2, k3, k4 = st.columns(4)
        k1.metric("下雨天平均日營收", _safe_currency(rainy_revenue))
        k2.metric("非雨天平均日營收", _safe_currency(normal_revenue))
        k3.metric("高溫天平均日營收", _safe_currency(hot_revenue))
        k4.metric("低溫天平均日營收", _safe_currency(cold_revenue))
        if temp_note:
            st.caption(f"ℹ️ {temp_note}")

        st.plotly_chart(
            px.scatter(
                daily,
                x="平均氣溫°C",
                y="每日營收",
                color="是否下雨" if "是否下雨" in daily.columns else None,
                hover_data=[col for col in ["transaction_date", "store_location", "降雨量mm"] if col in daily.columns],
                title="氣溫、降雨與每日營收關係"
            ),
            use_container_width=True
        )

        st.plotly_chart(
            px.bar(
                daily.sort_values("transaction_date"),
                x="transaction_date",
                y="每日營收",
                color="是否下雨" if "是否下雨" in daily.columns else None,
                title="每日營收與雨天變化"
            ),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("🥤 下雨天 / 高溫天 / 低溫天 商品影響")

    category_summary = _category_weather_summary(feature_df)
    if not category_summary.empty:
        metric_col = "營收" if "營收" in category_summary.columns else "銷量"
        st.plotly_chart(
            px.bar(
                category_summary,
                x="商品類別",
                y=metric_col,
                color="天氣類型",
                barmode="group",
                title="不同天氣類型下的商品類別表現"
            ),
            use_container_width=True
        )
        st.dataframe(category_summary, use_container_width=True, height=280)
    else:
        st.info("資料缺少 product_category 或銷售欄位，無法產生商品天氣分析。")

    st.markdown("---")
    st.subheader("⏰ 天氣對尖峰時段與來客量代理的影響")

    if "hour" in feature_df.columns and "Total_Bill" in feature_df.columns:
        hour_df = feature_df.copy()
        hour_df["天氣類型"] = "一般天氣"
        if "is_rainy_day" in hour_df.columns:
            hour_df.loc[hour_df["is_rainy_day"] == 1, "天氣類型"] = "下雨天"
        if "is_hot_weather" in hour_df.columns:
            hour_df.loc[hour_df["is_hot_weather"] == 1, "天氣類型"] = "高溫天"

        hour_summary = (
            hour_df
            .groupby(["hour", "天氣類型"], dropna=False)
            .agg(
                營收=("Total_Bill", "sum"),
                交易筆數=("Total_Bill", "count"),
                銷量=("transaction_qty", "sum") if "transaction_qty" in hour_df.columns else ("Total_Bill", "count")
            )
            .reset_index()
        )

        st.plotly_chart(
            px.line(
                hour_summary,
                x="hour",
                y="交易筆數",
                color="天氣類型",
                markers=True,
                title="天氣影響每小時來客量代理（交易筆數）"
            ),
            use_container_width=True
        )

        st.plotly_chart(
            px.line(
                hour_summary,
                x="hour",
                y="營收",
                color="天氣類型",
                markers=True,
                title="天氣影響每小時營收與尖峰時段"
            ),
            use_container_width=True
        )

    st.markdown("---")
    st.subheader("🤖 AI 商業洞察")

    insights = []
    if "is_rainy_day" in feature_df.columns and feature_df["is_rainy_day"].mean() > 0:
        insights.append("雨天可提高熱飲、外送、外帶與快速取餐備貨，並觀察尖峰是否從通勤時段轉向中午或午後。")
    if "is_hot_weather" in feature_df.columns and feature_df["is_hot_weather"].mean() > 0:
        insights.append("高溫天建議增加冰飲、冷萃、茶飲與清爽類商品備貨。")
    if "is_cold_weather" in feature_df.columns and feature_df["is_cold_weather"].mean() > 0:
        insights.append("低溫天建議增加熱咖啡、熱拿鐵、茶類與早餐組合，提高客單價。")
    insights.append("預測模型已可使用天氣 + 假日 + 時段 + 門市 + 商品類別等特徵進行營收預測。")

    for item in insights:
        st.success("✅ " + item)


    with st.expander("下載目前整合後的天氣特徵 CSV"):
        export_df = feature_df.copy()
        csv_bytes = export_df.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig")
        st.download_button(
            "下載 Coffee_Shop_Enterprise_Features_Cleaned.csv",
            data=csv_bytes,
            file_name="Coffee_Shop_Enterprise_Features_Cleaned.csv",
            mime="text/csv",
        )

    with st.expander("查看天氣特徵欄位"):
        weather_cols = [
            col for col in feature_df.columns
            if "weather" in col.lower() or col in [
                "avg_temp_c", "rain_prob", "is_rainy_day", "is_hot_weather", "is_cold_weather",
                "is_heavy_rain_day", "is_snow_day", "comfort_temp_score"
            ]
        ]
        st.dataframe(feature_df[weather_cols].head(200), use_container_width=True)

    with st.expander("查看即時三店天氣 API 狀態"):
        if st.button("讀取目前天氣"):
            try:
                current_weather = get_all_current_weather()
                st.dataframe(current_weather, use_container_width=True)
            except Exception as exc:
                st.error("即時天氣讀取失敗")
                st.code(str(exc))
