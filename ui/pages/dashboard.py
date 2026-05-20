import streamlit as st
import pandas as pd
import plotly.express as px
from utils.shared_data import get_shared_clean_data
from utils.schema import ensure_required_columns


def run_dashboard_page():
    st.title("📊 KPI / 尖峰 / 營收統計")
    st.caption("本頁使用左側全平台共用 CSV。")

    try:
        df, source_name = get_shared_clean_data(prefer_feature=True)
    except Exception as e:
        st.error("❌ 儀錶板資料處理失敗")
        st.code(str(e))
        return
    if df is None or df.empty:
        st.info("請先在左側上傳 CSV。")
        return

    df = ensure_required_columns(df.copy())
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date", "total_amount"])
    df["date"] = df["transaction_date"].dt.date
    df["hour"] = pd.to_numeric(df.get("hour", 0), errors="coerce").fillna(0).astype(int).clip(0, 23)

    st.success(f"✅ 資料載入成功：{source_name}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總營收", f"${df['total_amount'].sum():,.0f}")
    c2.metric("交易筆數", f"{len(df):,}")
    c3.metric("平均客單價", f"${df['total_amount'].mean():.2f}")
    c4.metric("門市數", f"{df['store_location'].nunique():,}")

    daily = df.groupby("date", as_index=False)["total_amount"].sum().rename(columns={"date":"日期", "total_amount":"營收"})
    st.subheader("每日營收")
    st.plotly_chart(px.line(daily, x="日期", y="營收", markers=True), use_container_width=True)

    hourly = df.groupby("hour", as_index=False)["total_amount"].sum().rename(columns={"hour":"小時", "total_amount":"營收"})
    st.subheader("每小時營收（尖峰分析）")
    st.plotly_chart(px.bar(hourly, x="小時", y="營收", text="營收"), use_container_width=True)

    store = df.groupby("store_location", as_index=False).agg(總營收=("total_amount","sum"), 交易筆數=("total_amount","count"), 平均客單價=("total_amount","mean")).sort_values("總營收", ascending=False).rename(columns={"store_location":"門市"})
    st.subheader("三家店營收比較")
    st.dataframe(store, use_container_width=True)
    st.plotly_chart(px.bar(store, x="門市", y="總營收", text="總營收"), use_container_width=True)

    with st.expander("查看清洗後資料與欄位"):
        st.write(list(df.columns))
        st.dataframe(df.head(100), use_container_width=True)
