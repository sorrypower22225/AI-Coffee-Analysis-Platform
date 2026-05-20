import streamlit as st

# ====================================
# 頁面設定
# ====================================

st.set_page_config(
    page_title="公式計算器",
    page_icon="🧮",
    layout="wide"
)

# ====================================
# 標題
# ====================================

st.title("🧮 Enterprise Formula Calculator")

st.markdown("---")

# ====================================
# 模式選擇
# ====================================

mode = st.selectbox(

    "選擇公式模式",

    [
        "Y = X × R",
        "X = Y ÷ R"
    ]

)

# ====================================
# Y = X × R
# ====================================

if mode == "Y = X × R":

    st.subheader("📈 計算 Y")

    col1, col2 = st.columns(2)

    with col1:

        X = st.number_input(
            "輸入 X",
            value=0.0
        )

    with col2:

        R = st.number_input(
            "輸入 R",
            value=0.0
        )

    if st.button("開始計算"):

        Y = X * R

        st.success(
            f"✅ 計算結果 Y = {Y:,.2f}"
        )

# ====================================
# X = Y ÷ R
# ====================================

elif mode == "X = Y ÷ R":

    st.subheader("📉 反推 X")

    col1, col2 = st.columns(2)

    with col1:

        Y = st.number_input(
            "輸入 Y",
            value=0.0
        )

    with col2:

        R = st.number_input(
            "輸入 R",
            value=1.0
        )

    if st.button("開始反推"):

        if R == 0:

            st.error("❌ R 不可為 0")

        else:

            X = Y / R

            st.success(
                f"✅ 計算結果 X = {X:,.2f}"
            )

# ====================================
# 顯示公式
# ====================================

st.markdown("---")

st.latex(r"Y = X \times R")

st.latex(r"X = \frac{Y}{R}")