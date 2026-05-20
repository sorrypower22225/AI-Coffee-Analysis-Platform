# AI Coffee Ultimate｜外部特徵因子企業級整合版

本版已整合至：

- `services/features_service.py`
- `services/forecasting_service.py`
- `ui/pages/forecast.py`

## 已加入外部特徵因子

1. 日期週期特徵：年、月、日、星期、週數、季度、月初、月底、週期 sin/cos
2. 假日特徵：美國國定假日、假日前一天、假日後一天
3. 商業檔期：薪資日、月中、聖誕季、黑五期間、學期、暑假
4. 天氣代理因子：紐約月均溫、降雨機率、冷天、熱天、舒適溫度分數
5. 門市位置因子：通勤分數、觀光分數、辦公區分數、位置類型
6. 時段需求：早上、午餐、下午、晚上、尖峰、離峰、通勤尖峰
7. 商品情境：咖啡、茶、食品、飲品、冷天熱飲適配、早晨咖啡適配
8. 滯後趨勢：前一日門市營收、前七日門市營收、七日移動平均
9. 安全類別編碼：所有文字欄位自動產生 `_code` 欄位

## 重要設計

預設不使用 `transaction_qty` 與 `unit_price` 當正式預測特徵，避免模型直接看到答案造成分數虛高。
如果只是要解釋單筆交易金額，可在預測頁勾選「允許使用 transaction_qty 與 unit_price」。

## 執行方式

```bash
streamlit run app.py
```

## 測試結果

已用專案內 `data/Coffee Shop Sales.csv` 測試：

- 特徵工程可正常執行
- `prepare_model_data()` 可正常產生模型資料
- `run_single_model_backtest()` 可正常完成 RandomForest 回測
- `py_compile` 語法檢查通過
