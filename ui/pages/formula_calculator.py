import streamlit as st


def run_formula_calculator_page():

    st.title("🧮 公式計算器")

    st.markdown("---")

    mode = st.selectbox(
        "選擇公式模式",
        [
            "Y = X × R",
            "X = Y ÷ R"
        ]
    )

    # =========================
    # 計算 Y
    # =========================
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

        if st.button("開始計算 Y"):

            Y = X * R

            st.success(
                f"✅ Y = {Y:,.2f}"
            )

    # =========================
    # 反推 X
    # =========================
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

        if st.button("開始反推 X"):

            if R == 0:

                st.error("❌ R 不可為 0")

            else:

                X = Y / R

                st.success(
                    f"✅ X = {X:,.2f}"
                )

    st.markdown("---")

    st.latex(r"Y = X \times R")
    st.latex(r"X = \frac{Y}{R}")