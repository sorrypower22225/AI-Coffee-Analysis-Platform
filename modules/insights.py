import pandas as pd

# =========================
# AI 商業洞察
# =========================

def generate_insights(df):

    insights = []

    # =========================
    # 總營收
    # =========================

    total_sales = df['Total_Bill'].sum()

    insights.append(
        f"☕ 總營收為 ${total_sales:,.0f}"
    )

    # =========================
    # 尖峰時段
    # =========================

    peak_hour = (
        df.groupby('Hour')['Total_Bill']
        .sum()
        .idxmax()
    )

    insights.append(
        f"🔥 尖峰時段為 {peak_hour}:00"
    )

    # =========================
    # 熱門商品
    # =========================

    top_product = (
        df.groupby('product_detail')
        ['transaction_qty']
        .sum()
        .idxmax()
    )

    insights.append(
        f"🥤 熱門商品為 {top_product}"
    )

    # =========================
    # 平均客單價
    # =========================

    avg_bill = df['Total_Bill'].mean()

    insights.append(
        f"💰 平均客單價為 ${avg_bill:.2f}"
    )

    # =========================
    # 假日分析
    # =========================

    weekend_sales = (
        df[df['Is_Weekend'] == True]
        ['Total_Bill']
        .mean()
    )

    weekday_sales = (
        df[df['Is_Weekend'] == False]
        ['Total_Bill']
        .mean()
    )

    if weekend_sales > weekday_sales:

        insights.append(
            "📈 假日營收較高，可增加人力配置"
        )

    else:

        insights.append(
            "📉 平日營收較高，可加強會員活動"
        )

    return insights