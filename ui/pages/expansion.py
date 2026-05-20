import os
import streamlit as st
import pandas as pd
import plotly.express as px

from services.cleaning_service import clean_data
from services.expansion_service import (
    calculate_store_scores,
    calculate_store_hour_product_profile,
    predict_fourth_store_candidates,
    expansion_ai_model,
)


from utils.data_loader import load_default_data, read_csv_safely


def _load_default_csv():
    return load_default_data(prefer_feature=True)


def run_expansion_page():
    st.title("🏪 三家店分析 + 第四家店展店預測")
    st.caption("依據現有三家店營收、銷量、客單價、尖峰時段與商品結構，推估第四家店候選區域。")

    from utils.shared_data import get_shared_clean_data
    try:
        df, source_name = get_shared_clean_data(prefer_feature=True)
    except Exception as e:
        st.error("❌ 展店分析資料清洗失敗")
        st.code(str(e))
        return
    if df is None or df.empty:
        st.info("請先在左側上傳 CSV。")
        return
    st.success(f"✅ 目前使用資料：{source_name}")

    try:
        score = calculate_store_scores(df)
        profile = calculate_store_hour_product_profile(df)
        candidates = predict_fourth_store_candidates(df)
    except Exception as e:
        st.error("❌ 展店分析失敗")
        st.code(str(e))
        return

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("目前門市數", f"{df['store_location'].nunique():,}")
    c2.metric("三店總營收", f"${df['total_amount'].sum():,.0f}")
    c3.metric("平均客單價", f"${df['total_amount'].mean():.2f}")
    c4.metric("最佳門市", str(score.iloc[0]["store_location"]))

    st.subheader("📊 三家店商圈評分")
    st.dataframe(score, use_container_width=True)
    fig = px.bar(score, x="store_location", y="商圈分數", text="商圈分數", title="三家店商圈分數比較")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("⏰ 每店尖峰小時與主力商品")
    st.dataframe(profile, use_container_width=True)

    st.subheader("🏪 第四家店候選區域預測")
    show_cols = ["第四家店候選區域", "定位", "展店總分", "第四家店成功率", "預估每日營收", "預估月營收", "預估客單價", "rent_risk", "competition_risk"]
    st.dataframe(candidates[show_cols], use_container_width=True)
    fig2 = px.bar(candidates, x="第四家店候選區域", y="展店總分", text="展店總分", title="第四家店候選區域排名")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("🤖 AI 展店建議")
    st.markdown(expansion_ai_model(df))


def show_expansion():
    run_expansion_page()
