import streamlit as st
import pandas as pd
import plotly.express as px

from services.db import load_data


def show_inventory():

    st.title(
        "📦 AI庫存管理"
    )

    # ==========================
    # 讀取資料
    # ==========================

    try:

        df = load_data()

        st.success(
            "成功讀取 MySQL"
        )

    except Exception as e:

        st.error(
            f"資料讀取失敗: {e}"
        )

        return

    # ==========================
    # 檢查必要欄位
    # ==========================

    need_cols=[

        "product_detail",
        "transaction_qty"

    ]

    missing=[

        c for c in need_cols
        if c not in df.columns

    ]

    if missing:

        st.error(
            f"缺少欄位: {missing}"
        )

        st.write(
            "目前欄位："
        )

        st.write(
            list(df.columns)
        )

        return

    # ==========================
    # 空值處理
    # ==========================

    df=df.dropna(
        subset=[
            "product_detail",
            "transaction_qty"
        ]
    )

    if len(df)==0:

        st.warning(
            "沒有資料"
        )

        return

    # ==========================
    # 建立庫存分析
    # ==========================

    stock=(

        df.groupby(
            "product_detail"
        )["transaction_qty"]

        .sum()

        .reset_index()

    )

    stock.columns=[

        "商品",
        "銷售數量"

    ]

    # 模擬初始庫存

    stock["初始庫存"]=1000

    stock["目前庫存"]=(
        stock["初始庫存"]
        -
        stock["銷售數量"]
    )

    stock["狀態"]="正常"

    stock.loc[

        stock[
            "目前庫存"
        ]<300,

        "狀態"

    ]="⚠️需補貨"

    # ==========================
    # KPI
    # ==========================

    total_items=len(
        stock
    )

    warning=len(

        stock[
            stock["狀態"]
            ==
            "⚠️需補貨"
        ]

    )

    avg_stock=stock[
        "目前庫存"
    ].mean()

    c1,c2,c3=st.columns(3)

    c1.metric(
        "商品數",
        total_items
    )

    c2.metric(
        "需補貨",
        warning
    )

    c3.metric(
        "平均庫存",
        f"{avg_stock:,.0f}"
    )

    st.divider()

    # ==========================
    # 庫存表
    # ==========================

    st.subheader(
        "📋 商品庫存表"
    )

    st.dataframe(

        stock.sort_values(
            "目前庫存"
        )

    )

    st.divider()

    # ==========================
    # 庫存圖
    # ==========================

    st.subheader(
        "📊 商品庫存分析"
    )

    fig=px.bar(

        stock.sort_values(
            "目前庫存"
        ),

        x="商品",

        y="目前庫存",

        color="狀態",

        title="商品庫存狀況"

    )

    fig.update_layout(
        height=550
    )

    st.plotly_chart(

        fig,

        use_container_width=True

    )

    st.divider()

    # ==========================
    # TOP10熱銷
    # ==========================

    st.subheader(
        "🔥 TOP10熱銷商品"
    )

    top=(

        df.groupby(
            "product_detail"
        )["transaction_qty"]

        .sum()

        .sort_values(
            ascending=False
        )

        .head(10)

        .reset_index()

    )

    fig2=px.bar(

        top,

        x="product_detail",

        y="transaction_qty",

        title="TOP10熱銷商品"

    )

    st.plotly_chart(

        fig2,

        use_container_width=True

    )

    # ==========================
    # AI推薦
    # ==========================

    st.divider()

    st.subheader(
        "🤖 AI商品建議"
    )

    best=top.iloc[0][
        "product_detail"
    ]

    qty=top.iloc[0][
        "transaction_qty"
    ]

    low_stock=(

        stock
        .sort_values(
            "目前庫存"
        )
        .head(5)

    )

    st.success(

f"""
熱門商品：

{best}

銷量：

{qty:,}

AI建議：

• 優先補貨熱門商品
• 增加曝光版位
• 推出套餐組合
• 庫存低商品提前採購
"""

    )

    st.subheader(
        "⚠️ 最低庫存商品"
    )

    st.dataframe(

        low_stock[
            [
                "商品",
                "目前庫存",
                "狀態"
            ]
        ]

    )