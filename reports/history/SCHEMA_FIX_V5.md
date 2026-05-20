# Enterprise V5 Schema Fix

本版修正 Dashboard 上傳 Enterprise Feature CSV 後出現：

```text
None of ['transaction_date'] are in the columns
```

## 已完成

- 新增 `utils/schema.py`
- 全平台自動標準化欄位名稱
- 支援原始 CSV 與 Enterprise Feature CSV
- 修正 Dashboard 每日營收圖表
- 修正 forecast 預設讀取 Enterprise Feature CSV
- 保留 `transaction_date`、`total_amount`、`Total_Bill` 相容性

## 啟動

```bash
streamlit run app.py
```

上傳 `Coffee_Shop_Enterprise_Features_Cleaned.csv` 即可。
