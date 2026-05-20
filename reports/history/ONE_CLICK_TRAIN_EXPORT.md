# 一鍵訓練 + 一鍵測試 + 匯出模型 .pkl

## Streamlit 使用方式

```bash
streamlit run app.py
```

進入「預測分析」頁面後，上傳 CSV，按下：

```text
🚀 一鍵訓練 + 測試 + 匯出 .pkl
```

系統會輸出：

- `models/exported_latest/best_model.pkl`
- `models/exported_latest/Linear.pkl`
- `models/exported_latest/RandomForest.pkl`
- `models/exported_latest/XGBoost.pkl`
- `models/exported_latest/LightGBM.pkl`
- `models/exported_latest/CatBoost.pkl`
- `models/exported_latest/model_leaderboard.csv`
- `models/exported_latest/test_predictions.csv`
- `models/exported_latest/manifest.json`
- `models/exported_latest/exported_models.zip`

## CLI 使用方式

```bash
python train_export_models.py
```

## 安全規則

- 永遠移除 `Total_Bill / total_amount / future / target`
- 使用時間序列切分，`shuffle=False`
- 輸出 Train R²、Test R²、過擬合差距、RMSE、MAE、MAPE、±5/10/20% 正確率
- `.pkl` 內含模型、特徵欄位、指標、訓練設定
