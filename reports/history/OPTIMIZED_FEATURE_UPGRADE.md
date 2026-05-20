# AI Coffee Ultimate｜最佳化特徵升級版

本版已將預測模組升級為「模型專屬最佳化特徵」版本。

## 已完成

- 每種模型自動使用適合自己的安全特徵組
- Linear / Ridge / Lasso 使用較穩定的線性特徵
- RandomForest / GradientBoosting / XGBoost / LightGBM / CatBoost 使用樹模型最佳化特徵
- 保留合法商業特徵：transaction_qty、unit_price、時間、假日、天氣、尖峰、門市位置、商品情境、lag、rolling
- 永遠移除資料洩漏欄位：Total_Bill、total_amount、future、target、store_high_sales_day
- 時間排序後再切分，不使用 shuffle=True
- UI 新增特徵模式：optimized / all_safe
- UI 可查看各模型最佳化後實際使用特徵數
- modules/forecasting.py 也改為共用 services/forecasting_service.py 的最佳化特徵邏輯

## 建議使用

預測分析頁：

- 使用 transaction_qty 與 unit_price：勾選
- 特徵模式：每種模型自動使用最佳特徵組 optimized
- 天氣：可使用 Open-Meteo；若速度慢可關閉使用代理天氣

## 注意

R² 不應追求 0.99。若修正後落在 0.70～0.85，通常比 0.999 更可信。
