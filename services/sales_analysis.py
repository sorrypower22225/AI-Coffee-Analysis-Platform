# ui/pages/sales_analysis.py

import streamlit as st
import pandas as pd

def run_analysis_page():

    st.title("💰 營業分析")

    uploaded_file = st.file_uploader(
        "上傳 CSV 檔 (Sales Analysis)",
        type=['csv']
    )

    if uploaded_file:

        df = pd.read_csv(uploaded_file)

        # =========================
        # 建立營收
        # =========================
        df['total_amount'] = (
            df['transaction_qty']
            * df['unit_price']
        )

        # =========================
        # 每日營收
        # =========================
        daily_sales = (
            df.groupby('transaction_date')['total_amount']
            .sum()
            .reset_index()
        )

        st.subheader("📈 每日營收趨勢")

        st.line_chart(
            daily_sales.set_index(
                'transaction_date'
            )
        )

        # =========================
        # 每小時營收
        # =========================
        df['hour'] = pd.to_datetime(
            df['transaction_time'],
            errors='coerce'
        ).dt.hour

        peak_sales = (
            df.groupby('hour')['total_amount']
            .sum()
            .reset_index()
        )

        st.subheader("⏰ 每小時營收分析")

        st.bar_chart(
            peak_sales.set_index('hour')
        )

        # =========================
        # 商品分析
        # =========================
        st.subheader("☕ 商品營收 TOP10")

        top_products = (
            df.groupby('product_category')['total_amount']
            .sum()
            .sort_values(ascending=False)
            .head(10)
        )

        st.bar_chart(top_products)

        # =========================
        # 門市分析
        # =========================
        st.subheader("🏪 門市營收")

        store_sales = (
            df.groupby('store_location')['total_amount']
            .sum()
            .sort_values(ascending=False)
        )

        st.bar_chart(store_sales)

        # =========================
        # KPI
        # =========================
        st.subheader("📊 KPI")

        total_sales = df['total_amount'].sum()

        avg_sales = (
            df.groupby('transaction_date')['total_amount']
            .sum()
            .mean()
        )

        total_orders = len(df)

        col1, col2, col3 = st.columns(3)

        col1.metric(
            "總營收",
            f"${total_sales:,.0f}"
        )

        col2.metric(
            "平均每日營收",
            f"${avg_sales:,.0f}"
        )

        col3.metric(
            "交易筆數",
            f"{total_orders:,}"
        )