import streamlit as st
import pandas as pd
import plotly.express as px
from utils.shared_data import get_shared_clean_data


def run_analysis_page():
    st.title("📊 營業分析｜真實 CSV 數據")
    st.caption("本頁已改為讀取左側「全平台共用資料」，不再使用 demo 假資料。")

    try:
        df, source_name = get_shared_clean_data(prefer_feature=True)
    except Exception as e:
        st.error("❌ 營業分析資料清洗失敗")
        st.code(str(e))
        return

    if df is None or df.empty:
        st.info("請先在左側上傳 CSV，或確認 data 資料夾有內建 CSV。")
        return

    st.success(f"✅ 營業分析資料載入成功：{source_name}")

    df = df.copy()
    df["transaction_date"] = pd.to_datetime(df["transaction_date"], errors="coerce")
    df = df.dropna(subset=["transaction_date", "total_amount"])
    df["month"] = df["transaction_date"].dt.to_period("M").astype(str)
    df["date"] = df["transaction_date"].dt.date
    df["hour"] = pd.to_numeric(df.get("hour", 0), errors="coerce").fillna(0).astype(int).clip(0, 23)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("總營收", f"${df['total_amount'].sum():,.0f}")
    c2.metric("總交易筆數", f"{len(df):,}")
    c3.metric("平均客單價", f"${df['total_amount'].mean():.2f}")
    c4.metric("門市數", f"{df['store_location'].nunique():,}")

    st.subheader("每日營收趨勢")
    daily = df.groupby("date", as_index=False)["total_amount"].sum().rename(columns={"date":"日期", "total_amount":"營收"})
    st.dataframe(daily.head(20), use_container_width=True)
    st.plotly_chart(px.line(daily, x="日期", y="營收", markers=True), use_container_width=True)

    st.subheader("每月營收趨勢")
    monthly = df.groupby(["month", "store_location"], as_index=False)["total_amount"].sum().rename(columns={"month":"月份", "store_location":"門市", "total_amount":"營收"})
    st.plotly_chart(px.line(monthly, x="月份", y="營收", color="門市", markers=True), use_container_width=True)

    st.subheader("每小時營收 / 尖峰分析")
    hourly = df.groupby(["hour", "store_location"], as_index=False)["total_amount"].sum().rename(columns={"hour":"小時", "store_location":"門市", "total_amount":"營收"})
    st.plotly_chart(px.bar(hourly, x="小時", y="營收", color="門市", barmode="group"), use_container_width=True)

    st.subheader("三家店營收比較")
    store = df.groupby("store_location", as_index=False).agg(
        總營收=("total_amount", "sum"),
        交易筆數=("total_amount", "count"),
        平均客單價=("total_amount", "mean"),
        總銷量=("transaction_qty", "sum"),
    ).sort_values("總營收", ascending=False).rename(columns={"store_location":"門市"})
    st.dataframe(store, use_container_width=True)
    st.plotly_chart(px.bar(store, x="門市", y="總營收", text="總營收"), use_container_width=True)

    st.subheader("商品類別營收")
    cat = df.groupby(["product_category", "store_location"], as_index=False)["total_amount"].sum().rename(columns={"product_category":"商品類別", "store_location":"門市", "total_amount":"營收"})
    st.plotly_chart(px.bar(cat, x="商品類別", y="營收", color="門市", barmode="group"), use_container_width=True)

    with st.expander("查看目前資料欄位與前 100 筆"):
        st.write(list(df.columns))
        st.dataframe(df.head(100), use_container_width=True)
