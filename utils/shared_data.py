import streamlit as st
import pandas as pd
from utils.data_loader import load_default_data, read_csv_safely
from services.cleaning_service import clean_data

RAW_KEY = "__shared_raw_df"
CLEAN_KEY = "__shared_clean_df"
NAME_KEY = "__shared_data_name"


def set_shared_data(df: pd.DataFrame, name: str = "uploaded.csv"):
    st.session_state[RAW_KEY] = df.copy()
    st.session_state[CLEAN_KEY] = None
    st.session_state[NAME_KEY] = name


def has_shared_data() -> bool:
    return RAW_KEY in st.session_state and st.session_state[RAW_KEY] is not None


def get_shared_raw_data(prefer_feature: bool = True) -> tuple[pd.DataFrame | None, str]:
    if has_shared_data():
        return st.session_state[RAW_KEY].copy(), st.session_state.get(NAME_KEY, "上傳資料")
    df = load_default_data(prefer_feature=prefer_feature)
    if df is None:
        return None, ""
    return df, "內建範例資料"


def get_shared_clean_data(prefer_feature: bool = True) -> tuple[pd.DataFrame | None, str]:
    if has_shared_data() and st.session_state.get(CLEAN_KEY) is not None:
        return st.session_state[CLEAN_KEY].copy(), st.session_state.get(NAME_KEY, "上傳資料")
    raw, name = get_shared_raw_data(prefer_feature=prefer_feature)
    if raw is None:
        return None, name
    cleaned = clean_data(raw)
    if has_shared_data():
        st.session_state[CLEAN_KEY] = cleaned.copy()
    return cleaned, name


def sidebar_global_uploader():
    st.sidebar.markdown("---")
    st.sidebar.subheader("📁 全平台共用資料")
    uploaded = st.sidebar.file_uploader(
        "上傳 CSV 後，所有頁面會共用同一份資料",
        type=["csv"],
        key="global_csv_uploader",
    )
    if uploaded is not None:
        try:
            df = read_csv_safely(uploaded)
            set_shared_data(df, uploaded.name)
            st.sidebar.success(f"已載入：{uploaded.name}")
        except Exception as e:
            st.sidebar.error("CSV 讀取失敗")
            st.sidebar.code(str(e))
    elif has_shared_data():
        st.sidebar.success(f"目前資料：{st.session_state.get(NAME_KEY, '上傳資料')}")
    else:
        st.sidebar.info("尚未上傳，會使用內建範例 CSV。")

    if st.sidebar.button("清除上傳資料 / 改用內建資料"):
        st.session_state.pop(RAW_KEY, None)
        st.session_state.pop(CLEAN_KEY, None)
        st.session_state.pop(NAME_KEY, None)
        st.rerun()
