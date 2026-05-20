# ☕ AI 咖啡營運分析平台｜作品集優化版

## 🌐 線上展示網站

https://ai-coffee-analysis-platform.onrender.com

本專案已部署於 Render，可直接透過瀏覽器查看系統畫面。  
第一次開啟可能需要等待 30～60 秒，因為 Render Free 方案閒置後會自動休眠。

---

## 專案簡介

這是一個以咖啡店交易資料為基礎的商業智慧與 AI 預測專案，整合資料清洗、營收儀錶板、商品分析、天氣影響分析、AI 營收預測與展店 ROI 分析。

本專案目標是將原始交易資料轉換成可視化決策系統，模擬企業在營運管理、銷售分析、展店評估與 AI 預測上的應用場景。

---

## 專案目標

透過交易資料建立完整的營運分析系統，協助回答：

- 哪一家店營收表現最好？
- 哪些商品最適合主推？
- 尖峰與離峰時段如何影響營收？
- 天氣變化是否會影響門市營收？
- AI 模型能否預測未來營收？
- 第四家店應該優先考慮哪個區域？
- 如何將分析結果整理成可展示的作品集專案？

---

## 主要功能

- 營運 KPI 儀錶板
- 各門市營收比較
- 商品銷售分析
- 營業時段與尖離峰分析
- 天氣與銷售影響分析
- AI 營收預測與模型比較
- 展店 ROI 分析
- CSV 上傳測試功能
- 原始資料與清洗後資料分流管理
- Render 線上部署展示
- GitHub 專案版本管理

---

## 技術工具

- Python
- Pandas
- NumPy
- Streamlit
- Plotly
- Scikit-learn
- XGBoost
- SQLAlchemy
- Open-Meteo / Weather features
- Git / GitHub
- Render

---

## 專案結構

```text
AI_Coffee_Portfolio_Final/
├─ app.py
├─ config.py
├─ requirements.txt
├─ requirements_render.txt
├─ render.yaml
├─ runtime.txt
├─ run_app.bat
├─ .gitignore
│
├─ data/
│  ├─ Coffee Shop Sales_RAW.csv
│  ├─ Coffee_Shop_Demo.csv
│  ├─ location_data.csv
│  ├─ README_DATA.md
│  └─ weather_cache/
│
├─ services/
├─ utils/
├─ ui/
│  └─ pages/
├─ tests/
├─ reports/
├─ database/
├─ modules/
└─ screenshots/
```

---

## 本機執行方式

### 1. 安裝套件

```bash
pip install -r requirements.txt
```

### 2. 啟動系統

```bash
streamlit run app.py
```

### 3. Windows 快速啟動

也可以直接執行：

```bat
run_app.bat
```

---

## Render 部署設定

本專案已部署於 Render。

### Build Command

```bash
pip install -r requirements_render.txt
```

### Start Command

```bash
streamlit run app.py --server.port $PORT --server.address 0.0.0.0
```

### 部署網址

```text
https://ai-coffee-analysis-platform.onrender.com
```

---

## 資料說明

完整資料放在 `data/`，詳細說明請看：

```text
data/README_DATA.md
```

GitHub 版本主要保留展示用資料，例如：

```text
Coffee_Shop_Demo.csv
location_data.csv
Coffee Shop Sales_RAW.csv
```

大型清洗後資料可保留於本機版本，用於完整分析、模型訓練與 Power BI 分析，避免 GitHub 上傳超過檔案限制。

---

## 優化重點

本版本已完成：

- 移除重複 CSV
- 移除 `__pycache__` 與 `.pyc`
- 新增 `.gitignore`
- 新增 `config.py` 統一管理路徑
- 新增 `requirements_render.txt`
- 修正 Render 部署設定
- 整理測試腳本到 `tests/`
- 建立資料說明與優化報告
- 修正重複欄位問題
- 修正天氣分析 `nan` 顯示問題
- 完成 GitHub 上傳
- 完成 Render 公開部署

---

## 專案成果

本專案可作為：

- 資料分析作品集
- Python / Streamlit 專案展示
- AI 預測模型展示
- 商業智慧 Dashboard 展示
- 履歷與面試作品展示
- GitHub 專案管理展示
- Render 雲端部署展示

---

## 線上與原始碼

### GitHub Repository

```text
https://github.com/sorrypower22225/AI-Coffee-Analysis-Platform
```

### Render Live Demo

```text
https://ai-coffee-analysis-platform.onrender.com
```

---

## 備註

本專案使用的 Coffee Shop Sales 資料為範例交易資料，適合作為資料分析、AI 預測、Power BI、Streamlit 與商業智慧作品集展示用途。