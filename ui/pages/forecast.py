
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

import streamlit as st
import pandas as pd
import numpy as np

from services.cleaning_service import clean_data
from services.features_service import build_feature_catalog, classify_feature_group
from services.forecasting_service import (
    MODELS,
    prepare_model_data,
    run_single_model_backtest,
    calculate_global_feature_importance,
    run_optuna_automl_search,
)
from utils.data_loader import load_default_data, read_csv_safely


def _load_default_csv():
    return load_default_data(prefer_feature=True)

def _feature_importance_df(row, features, top_n=65):
    fi = row.get("feature_importance")
    if fi is None or features is None:
        return pd.DataFrame()
    fi = np.array(fi, dtype=float)
    min_len = min(len(features), len(fi))
    df = pd.DataFrame({"特徵": list(features)[:min_len], "重要性": fi[:min_len]})
    df["重要性"] = pd.to_numeric(df["重要性"], errors="coerce").fillna(0)
    df = df.sort_values("重要性", ascending=False).head(top_n).reset_index(drop=True)
    df.insert(0, "排名", range(1, len(df) + 1))
    df["特徵類型"] = df["特徵"].apply(classify_feature_group)
    return df


def _render_model_feature_usage(model_features_map):
    st.subheader("🧩 每一種模型使用的特徵 TOP65")
    rows = []
    for model_name, features in model_features_map.items():
        for i, f in enumerate(features[:65], start=1):
            rows.append({"模型": model_name, "排名": i, "使用特徵": f, "特徵類型": classify_feature_group(f)})
    usage_df = pd.DataFrame(rows)
    if usage_df.empty:
        st.warning("尚無模型特徵資料。")
        return
    st.dataframe(usage_df, use_container_width=True, height=420)
    summary = usage_df.groupby(["模型", "特徵類型"]).size().reset_index(name="使用數量")
    with st.expander("查看每個模型使用的特徵類型統計"):
        st.dataframe(summary, use_container_width=True, height=300)


def _render_feature_importance_all(final_df, model_features_map):
    st.subheader("🏆 特徵重要性 TOP65")
    best_model = final_df.drop(columns=["feature_importance"], errors="ignore").sort_values("R2平均", ascending=False).index[0]
    top_df = _feature_importance_df(final_df.loc[best_model], model_features_map.get(best_model), top_n=65)
    if top_df.empty:
        st.warning("目前最佳模型不支援特徵重要性。")
        return []
    st.caption(f"目前顯示最佳模型：{best_model}")
    st.dataframe(top_df, use_container_width=True, height=520)
    chart_df = top_df.head(20).set_index("特徵")[["重要性"]]
    st.bar_chart(chart_df)
    with st.expander("依特徵類型統計重要性"):
        group_df = top_df.groupby("特徵類型", as_index=False)["重要性"].sum().sort_values("重要性", ascending=False)
        st.dataframe(group_df, use_container_width=True)
        st.bar_chart(group_df.set_index("特徵類型"))
    return top_df.head(12)["特徵"].tolist()


def _render_business_insights(top_features):
    st.subheader("💡 AI 自動商業洞察")
    top = set(top_features)
    insights = []
    if any("store" in f or "location" in f for f in top):
        insights.append("店面聚合特徵進入重要排名，代表不同門市的客群、位置與尖峰型態對營收有明顯影響。")
    if any("product" in f or "category" in f or "type" in f or "popularity" in f for f in top):
        insights.append("商品聚合與商品熱門度是重要因素，建議針對高人氣品項做套餐、加購與補貨策略。")
    if any("lag" in f or "rolling" in f for f in top):
        insights.append("多層 lag / rolling 特徵有效，代表近期銷售趨勢可以用來規劃隔日備料、排班與庫存。")
    if any("sin" in f or "cos" in f or "hour" in f or "weekday" in f for f in top):
        insights.append("週期時間特徵有效，代表營收有明顯小時、星期與月份規律。")
    if any("peak" in f for f in top):
        insights.append("每店尖峰特徵有影響，建議依門市尖峰時段分別制定人力與促銷策略。")
    if any("weather" in f or "rain" in f or "temp" in f for f in top):
        insights.append("天氣特徵有影響，冷熱天與雨天可調整熱飲、冰飲、外帶與庫存配置。")
    if not insights:
        insights.append("目前模型顯示多種因素共同影響營收，可優先觀察 TOP65 特徵中排名最高的店面、商品與時間因素。")
    for i, text in enumerate(insights, 1):
        st.write(f"{i}. {text}")


def run_forecast_page():
    st.title("☕ Enterprise AI 預測引擎 v3｜Feature Importance + Optuna AutoML")
    st.caption("已整合：全域特徵重要性、低貢獻特徵偵測、Optuna 自動搜尋最佳模型 / 參數 / 特徵數。")

    from utils.shared_data import get_shared_raw_data
    df, source_name = get_shared_raw_data(prefer_feature=True)
    if df is None or df.empty:
        st.info("請先在左側上傳 CSV，或確認 data 資料夾有內建 CSV。")
        return
    st.success(f"✅ 目前使用資料：{source_name}")

    try:
        cleaned_df = clean_data(df)
    except Exception as e:
        st.error("❌ 統一資料清洗失敗")
        st.code(str(e))
        return

    c1, c2, c3 = st.columns(3)
    c1.metric("清洗後資料筆數", f"{len(cleaned_df):,}")
    c2.metric("平均交易金額", f"${cleaned_df['total_amount'].mean():.2f}")
    c3.metric("總營收", f"${cleaned_df['total_amount'].sum():,.0f}")
    with st.expander("查看清洗後資料預覽"):
        st.dataframe(cleaned_df.head(30), height=260, use_container_width=True)

    st.markdown("---")
    st.subheader("⚙️ AI 引擎設定")
    col_a, col_b, col_c, col_d = st.columns(4)
    with col_a:
        n_iter = st.slider("隨機回測次數", min_value=1, max_value=10, value=5)
    with col_b:
        top_n_features = st.slider("每個模型最多使用特徵數", min_value=20, max_value=120, value=65, step=5)
    with col_c:
        use_real_weather = st.checkbox("使用真實歷史天氣 API", value=True)
    with col_d:
        add_business_aggregates = st.checkbox("啟用店面/商品聚合特徵", value=True)
    allow_target_leakage = st.checkbox("允許 transaction_qty / unit_price 進模型（不建議正式預測）", value=False)
    force_refresh_weather = st.checkbox("重新下載天氣資料", value=False)

    try:
        X_preview, y_preview, cat_features = prepare_model_data(
            cleaned_df,
            allow_target_leakage=allow_target_leakage,
            use_real_weather=use_real_weather,
            force_refresh_weather=force_refresh_weather,
            top_n_features=top_n_features,
            model_name="CatBoost",
            add_business_aggregates=add_business_aggregates,
        )
        p1, p2, p3, p4 = st.columns(4)
        p1.metric("模型可用筆數", f"{len(X_preview):,}")
        p2.metric("特徵數", f"{X_preview.shape[1]:,}")
        p3.metric("可用模型數", f"{len(MODELS):,}")
        p4.metric("CatBoost 類別特徵", f"{len(cat_features):,}")
        with st.expander("查看 65 特徵清單 / CatBoost categorical"):
            catalog = build_feature_catalog(X_preview.columns)
            st.dataframe(catalog, use_container_width=True, height=360)
            if cat_features:
                st.write("CatBoost categorical features：", ", ".join(cat_features))
    except Exception as e:
        st.error("❌ features_service / prepare_model_data 檢查失敗")
        st.code(str(e))
        return

    st.markdown("---")
    st.subheader("🧠 Feature Importance / Optuna AutoML")
    fi_col, opt_col = st.columns(2)
    with fi_col:
        if st.button("1️⃣ 計算全域特徵重要性 / 找出低貢獻特徵"):
            with st.spinner("正在計算全部特徵重要性..."):
                try:
                    fi_result = calculate_global_feature_importance(
                        cleaned_df,
                        allow_target_leakage=allow_target_leakage,
                        use_real_weather=use_real_weather,
                        force_refresh_weather=False,
                        add_business_aggregates=add_business_aggregates,
                    )
                    st.success(
                        f"完成：全部 {fi_result['n_total_features']} 個特徵，建議保留 {fi_result['n_keep_features']} 個，"
                        f"可觀察/移除 {fi_result['n_useless_features']} 個。"
                    )
                    st.dataframe(fi_result["importance_df"], use_container_width=True, height=520)
                    st.bar_chart(fi_result["importance_df"].head(20).set_index("特徵")[["重要性"]])
                    with st.expander("查看可考慮移除 / 觀察的低貢獻特徵"):
                        st.write(fi_result["useless_features"])
                except Exception as e:
                    st.error("Feature Importance 計算失敗")
                    st.code(str(e))
    with opt_col:
        optuna_trials = st.slider("Optuna 搜尋次數", min_value=5, max_value=40, value=15, step=5)
        if st.button("2️⃣ 執行 Optuna AutoML 搜尋最佳模型 / 參數 / 特徵數"):
            with st.spinner("Optuna 搜尋中，請稍候..."):
                try:
                    opt_result = run_optuna_automl_search(
                        cleaned_df,
                        n_trials=optuna_trials,
                        allow_target_leakage=allow_target_leakage,
                        use_real_weather=use_real_weather,
                        force_refresh_weather=False,
                        add_business_aggregates=add_business_aggregates,
                        candidate_models=[m for m in ["RandomForest", "ExtraTrees", "GradientBoosting", "XGBoost"] if m in MODELS],
                    )
                    st.success(
                        f"🏆 Optuna 最佳模型：{opt_result['best_model']}｜最佳特徵數：{opt_result['best_top_n_features']}｜"
                        f"R²：{opt_result['best_r2']:.4f}｜RMSE：{opt_result['best_rmse']:.2f}"
                    )
                    st.write("最佳參數：")
                    st.json(opt_result["best_params"])
                    st.write("Optuna Trial 排行：")
                    st.dataframe(opt_result["trials_df"], use_container_width=True, height=360)
                    st.write("最佳模型特徵重要性 TOP 30：")
                    st.dataframe(opt_result["feature_importance_df"].head(30), use_container_width=True, height=420)
                    st.bar_chart(opt_result["feature_importance_df"].head(20).set_index("特徵")[["重要性"]])
                except ImportError as e:
                    st.error("尚未安裝 Optuna。請重新安裝 requirements.txt 後再執行。")
                    st.code(str(e))
                except Exception as e:
                    st.error("Optuna AutoML 搜尋失敗")
                    st.code(str(e))

    selected_models = st.multiselect("選擇要比較的模型", options=list(MODELS.keys()), default=list(MODELS.keys()))
    if not selected_models:
        st.warning("請至少選擇一個模型。")
        return

    if st.button("🚀 執行企業級多模型回測", type="primary"):
        progress_text = st.empty()
        progress_bar = st.progress(0)
        result_placeholder = st.empty()
        best_placeholder = st.empty()
        total_steps = len(selected_models) * n_iter
        step_counter = 0
        results = {}
        model_features_map = {}
        model_cat_map = {}

        for model_index, model_name in enumerate(selected_models):
            r2_list, rmse_list, mae_list, fi_list = [], [], [], []
            for iter_index in range(n_iter):
                progress_text.info(f"正在訓練：{model_name}｜模型 {model_index + 1}/{len(selected_models)}｜回測 {iter_index + 1}/{n_iter}")
                try:
                    single = run_single_model_backtest(
                        df=cleaned_df,
                        model_name=model_name,
                        random_state=(iter_index + 1) * 42,
                        allow_target_leakage=allow_target_leakage,
                        use_real_weather=use_real_weather,
                        force_refresh_weather=False,
                        top_n_features=top_n_features,
                        add_business_aggregates=add_business_aggregates,
                    )
                    r2_list.append(single["r2"])
                    rmse_list.append(single["rmse"])
                    mae_list.append(single["mae"])
                    model_features_map[model_name] = single.get("features", [])
                    model_cat_map[model_name] = single.get("cat_features", [])
                    if single.get("feature_importance") is not None:
                        fi_list.append(np.array(single["feature_importance"], dtype=float))
                except Exception as e:
                    st.warning(f"⚠️ {model_name} 第 {iter_index + 1} 次回測失敗：{e}")

                if r2_list:
                    results[model_name] = {
                        "R2平均": float(np.mean(r2_list)),
                        "R2標準差": float(np.std(r2_list)),
                        "RMSE平均": float(np.mean(rmse_list)),
                        "RMSE標準差": float(np.std(rmse_list)),
                        "MAE平均": float(np.mean(mae_list)),
                        "使用特徵數": len(model_features_map.get(model_name, [])),
                        "CatBoost類別特徵數": len(model_cat_map.get(model_name, [])),
                        "feature_importance": np.mean(fi_list, axis=0) if fi_list else None,
                    }
                    live_df = pd.DataFrame(results).T.sort_values("R2平均", ascending=False)
                    result_placeholder.dataframe(live_df.drop(columns=["feature_importance"], errors="ignore"), use_container_width=True, height=320)
                    best_placeholder.success(f"目前最佳模型：{live_df.index[0]}｜R²：{live_df.iloc[0]['R2平均']:.4f}")
                step_counter += 1
                progress_bar.progress(min(step_counter / total_steps, 1.0))

        progress_text.success("✅ 全部模型訓練完成")
        if not results:
            st.error("❌ 所有模型皆訓練失敗，請檢查資料欄位。")
            return

        final_df = pd.DataFrame(results).T
        ranking_df = final_df.drop(columns=["feature_importance"], errors="ignore").sort_values("R2平均", ascending=False)
        st.subheader("📊 Model Comparison Dashboard｜模型排行榜")
        st.dataframe(ranking_df, use_container_width=True, height=360)
        st.write("R² 越高越好；RMSE / MAE 越低越好，因此分開顯示。")
        st.subheader("R² 平均（越高越好）")
        st.bar_chart(ranking_df[["R2平均"]])
        st.subheader("RMSE 平均（越低越好）")
        st.bar_chart(ranking_df[["RMSE平均"]])
        st.subheader("MAE 平均（越低越好）")
        st.bar_chart(ranking_df[["MAE平均"]])
        best_model = ranking_df.index[0]
        st.success(f"🏆 最佳模型：{best_model}｜R²：{ranking_df.loc[best_model, 'R2平均']:.4f}｜RMSE：{ranking_df.loc[best_model, 'RMSE平均']:.2f}")

        _render_model_feature_usage(model_features_map)
        top_features = _render_feature_importance_all(final_df, model_features_map)
        _render_business_insights(top_features)


if __name__ == "__main__":
    run_forecast_page()
