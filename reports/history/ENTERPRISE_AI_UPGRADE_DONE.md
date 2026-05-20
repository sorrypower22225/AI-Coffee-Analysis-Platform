# Enterprise AI Upgrade 完成說明

本版已完成以下 5 項升級：

1. 完整統一 `services/features_service.py`
   - 日期 / 時間特徵
   - 假日 / 節日前後 / 薪資日
   - 尖峰離峰
   - 天氣特徵
   - 門市位置特徵
   - 商品類型特徵
   - lag / rolling mean 特徵

2. 統一資料清洗 `services/cleaning_service.py`
   - 欄位標準化
   - 日期時間轉換
   - 數值轉換
   - 營收欄位統一為 `total_amount`
   - 移除缺失與異常營收資料

3. Model Comparison Dashboard
   - 支援 Linear / Ridge / Lasso / RandomForest / ExtraTrees / GradientBoosting
   - 若環境有安裝，也會自動加入 XGBoost / LightGBM / CatBoost

4. Feature Importance
   - 樹模型使用 `feature_importances_`
   - 線性模型使用 `coef_` 絕對值
   - 自動顯示 TOP 15 重要特徵

5. 即時訓練進度條
   - 每個模型、每次回測即時更新
   - 即時顯示目前排行榜與目前最佳模型

啟動方式：

```bash
streamlit run app.py
```

建議從最外層 `AI_Coffee_Ultimate` 資料夾執行。
