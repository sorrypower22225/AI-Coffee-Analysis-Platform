import streamlit as st
import pandas as pd
import plotly.express as px
from utils.shared_data import get_shared_clean_data


def run_analytics_page():
    st.title("🔎 商品 / 門市分析")
    st.caption("本頁使用左側全平台共用 CSV。")
    try:
        df, source_name = get_shared_clean_data(prefer_feature=True)
    except Exception as e:
        st.error("❌ 商品分析資料清洗失敗")
        st.code(str(e))
        return
    if df is None or df.empty:
        st.info("請先在左側上傳 CSV。")
        return
    st.success(f"✅ 資料載入成功：{source_name}")

    st.subheader("商品類別 TOP10 營收")
    top_categories = df.groupby("product_category", as_index=False)["total_amount"].sum().sort_values("total_amount", ascending=False).head(10).rename(columns={"product_category":"商品類別", "total_amount":"營收"})
    st.dataframe(top_categories, use_container_width=True)
    st.plotly_chart(px.bar(top_categories, x="商品類別", y="營收", text="營收"), use_container_width=True)

    st.subheader("商品品項 TOP15 營收")
    detail_col = "product_detail" if "product_detail" in df.columns else "product_type"
    top_products = df.groupby(detail_col, as_index=False)["total_amount"].sum().sort_values("total_amount", ascending=False).head(15).rename(columns={detail_col:"商品", "total_amount":"營收"})
    st.dataframe(top_products, use_container_width=True)
    st.plotly_chart(px.bar(top_products, x="商品", y="營收", text="營收"), use_container_width=True)

    st.subheader("各門市營收")
    store_sales = df.groupby("store_location", as_index=False)["total_amount"].sum().sort_values("total_amount", ascending=False).rename(columns={"store_location":"門市", "total_amount":"營收"})
    st.dataframe(store_sales, use_container_width=True)
    st.plotly_chart(px.bar(store_sales, x="門市", y="營收", text="營收"), use_container_width=True)

    st.subheader("各門市 × 商品類別營收")
    pivot = pd.pivot_table(df, values="total_amount", index="store_location", columns="product_category", aggfunc="sum", fill_value=0)
    st.dataframe(pivot, use_container_width=True)
