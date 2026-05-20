# Enterprise Expansion Fix V3

已修正：

- 儀錶板 `transaction_date` 欄位錯誤
- 統一資料清洗支援 BOM、空白、大小寫、Day of Week 等欄位別名
- Dashboard / 商品分析 / 展店分析都改用同一套 `clean_data()`
- 新增「展店分析 / 第四家店」頁面
- 三家店營收、客單價、尖峰、商品結構分析
- 第四家店候選區域預測：展店總分、成功率、預估每日/月營收
- 隱藏 Streamlit 內建重複 pages 導覽

啟動：

```bash
streamlit run app.py
```
