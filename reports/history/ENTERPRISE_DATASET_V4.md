# Enterprise Dataset V4

本版已完成整合：

- 已將 `Coffee_Shop_Enterprise_Features_Cleaned.csv` 放入 `data/`
- 已用新版 Feature CSV 更新 `data/Coffee Shop Sales.csv`，避免舊路徑讀取失敗
- 原始資料已備份為 `data/Coffee Shop Sales_RAW_BACKUP.csv`
- 所有頁面預設優先讀取 Enterprise Feature CSV
- 保留統一清洗引擎 `services/cleaning_service.py`
- 保留特徵工程引擎 `services/features_service.py`
- 預測頁支援 TOP65 特徵、Feature Importance、Model Comparison、即時進度條
- 展店頁支援三家店分析與第四家店候選區域預測

啟動方式：

```bash
streamlit run app.py
```
