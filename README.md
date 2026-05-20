# ☕ AI 咖啡營運分析平台｜作品集優化版

這是一個以咖啡店交易資料為基礎的商業智慧與 AI 預測專案，整合資料清洗、營收儀錶板、商品分析、天氣影響分析、AI 營收預測與展店 ROI 分析。

## 專案目標

透過交易資料建立完整的營運分析系統，協助回答：

- 哪一家店營收表現最好？
- 哪些商品最適合主推？
- 尖峰與離峰時段如何影響營收？
- AI 模型能否預測未來營收？
- 第四家店應該優先考慮哪個區域？

## 主要功能

- 營運 KPI 儀錶板
- 商品銷售分析
- 營業時段與尖離峰分析
- 天氣與銷售影響分析
- AI 營收預測與模型比較
- 展店 ROI 分析
- CSV 上傳測試功能
- 原始資料與清洗後資料分流管理

## 技術工具

- Python
- Pandas / NumPy
- Streamlit
- Plotly
- Scikit-learn
- XGBoost
- SQLAlchemy
- Open-Meteo / Weather features

## 專案結構

```text
AI_Coffee_Portfolio_Final/
├─ app.py
├─ config.py
├─ requirements.txt
├─ requirements_render.txt
├─ render.yaml
├─ data/
│  ├─ Coffee Shop Sales_RAW.csv
│  ├─ Coffee_Shop_Enterprise_Features_Corrected.csv
│  ├─ Coffee_Shop_Demo.csv
│  ├─ location_data.csv
│  └─ README_DATA.md
├─ services/
├─ utils/
├─ ui/pages/
├─ tests/
└─ reports/
```

## 本機執行

```bash
pip install -r requirements.txt
streamlit run app.py
```

Windows 也可以直接執行：

```bat
run_app.bat
```

## Render 部署

Render 建議使用輕量安裝檔：

```bash
pip install -r requirements_render.txt
```

`render.yaml` 已設定使用 `requirements_render.txt`。

## 資料說明

完整資料放在 `data/`，說明請看：

```text
data/README_DATA.md
```

GitHub 若不想放大型 CSV，可以只保留 `Coffee_Shop_Demo.csv`，並在 README 說明完整資料為本機展示版本。

## 優化重點

本版本已完成：

- 移除重複 CSV
- 移除 `__pycache__` 與 `.pyc`
- 新增 `config.py` 統一管理路徑
- 新增 `requirements_render.txt`
- 修正 Render 設定
- 整理測試腳本到 `tests/`
- 建立資料說明與優化報告
