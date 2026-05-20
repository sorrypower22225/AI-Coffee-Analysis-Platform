import streamlit as st


def show_home():

    st.title("☕ AI Coffee Ultimate")

    st.markdown(
        """
        ### 企業級 AI 智慧咖啡營運決策平台

        本系統整合咖啡店銷售資料、營收分析、AI 預測、
        庫存管理與展店分析，協助管理者快速掌握營運狀況。
        """
    )

    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    col1.metric("分析模組", "6")
    col2.metric("AI 模型", "3")
    col3.metric("決策面向", "營收 / 商品 / 門市")

    st.markdown("---")

    st.subheader("🚀 系統功能")

    col4, col5 = st.columns(2)

    with col4:
        st.success("✅ Dashboard：營運總覽與 KPI")
        st.success("✅ 營收分析：日期、時段、商品分析")
        st.success("✅ AI 預測：模型比較與營收預測")

    with col5:
        st.info("✅ 庫存管理：商品需求與補貨建議")
        st.info("✅ 展店分析：門市績效與展店決策")
        st.info("✅ 商業洞察：自動產生營運建議")

    st.markdown("---")

    st.subheader("📊 專案亮點")

    st.markdown(
        """
        - 使用 Streamlit 建立即時互動式商業儀表板
        - 使用 RandomForest、XGBoost、Linear Regression 進行模型比較
        - 分析營收趨勢、尖峰離峰、商品類別與門市績效
        - 自動產生企業級商業洞察與改善建議
        - 適合作為履歷作品集、GitHub 專案與面試展示
        """
    )

    st.markdown("---")

    st.subheader("🎯 建議操作流程")

    st.markdown(
        """
        1. 先查看「儀表板」掌握整體 KPI  
        2. 進入「營收分析」了解營收結構  
        3. 使用「AI預測」比較模型與預測結果  
        4. 查看「庫存管理」判斷商品補貨方向  
        5. 使用「展店分析」評估門市擴張機會  
        """
    )