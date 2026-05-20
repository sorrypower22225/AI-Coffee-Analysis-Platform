# AI 咖啡營運分析平台

本專案使用 Coffee Shop Sales 交易資料，建立一套結合資料清洗、商業智慧分析、Power BI Dashboard 與 AI 營收預測概念的咖啡店營運分析作品集。

> 資料來源為 Maven Analytics 提供的 fictitious coffee shop sales dataset，屬於虛構咖啡店交易資料，適合用於商業分析、AI 預測與作品集展示。

---

## 專案目標

本專案希望回答以下商業問題：

- 哪一家店營收表現最好？
- 哪些商品最值得主推？
- 尖峰與離峰時段對營收有什麼影響？
- 天氣變化是否會影響銷售？
- 如何透過資料建立更完整的營運決策儀表板？

---

## 專案內容

- 原始交易資料整理
- 分析用資料欄位標準化
- Power BI 專用資料集建立
- 營收 KPI 分析
- 店鋪績效分析
- 商品銷售分析
- 尖峰 / 離峰分析
- 天氣與營收影響分析
- Streamlit / Render 線上展示準備

---

## 專案架構

```text
AI_Coffee_GitHub_Ready/
│
├── data/
│   ├── Coffee_Shop_Sales_RAW.csv
│   └── Coffee_Shop_PowerBI_Dashboard_Data.csv
│
├── docs/
│   └── DATA_SUMMARY.json
│
├── powerbi/
│   ├── PowerBI_DAX_Measures.md
│   └── PowerBI_Dashboard_Guide.md
│
├── screenshots/
│   └── 放置 Power BI 或 Streamlit 截圖
│
├── scripts/
│   └── create_powerbi_data.py
│
├── models/
│   └── 放置訓練完成的模型檔案
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 資料說明

### `Coffee_Shop_Sales_RAW.csv`

原始交易資料，保留交易日期、時間、店鋪、商品、數量與金額等欄位。

### `Coffee_Shop_PowerBI_Dashboard_Data.csv`

Power BI 專用資料，已保留 Dashboard 需要的主要欄位，例如：

- 交易日期與時間
- 店鋪資訊
- 商品資訊
- 銷售數量
- 商品單價
- 總金額
- 尖峰 / 離峰狀態
- 天氣相關欄位

### 完整清洗資料說明

原本的完整清洗資料 `Coffee_Shop_Enterprise_Features_Corrected.csv` 約 263MB，超過 GitHub 一般單檔 100MB 限制，因此本 GitHub 版本不直接放入該大檔。

如果需要保存完整資料，建議：

1. 保存在本機，不上傳 GitHub。
2. 使用 Git LFS 管理大型檔案。
3. 只上傳 Power BI 專用精簡資料。

---

## Power BI Dashboard 規劃

建議建立 5 頁 Dashboard：

1. 營運總覽
2. 店鋪績效分析
3. 商品銷售分析
4. 尖峰離峰分析
5. 天氣與營收影響

詳細圖表配置請參考：

```text
powerbi/PowerBI_Dashboard_Guide.md
```

DAX 指標請參考：

```text
powerbi/PowerBI_DAX_Measures.md
```

---

## 核心商業洞察

- 尖峰時段可作為人力排班與備貨的重要依據。
- 店鋪之間的營收、訂單數與客單價差異，可用於門市營運優化。
- 商品銷售分析可以找出主力商品與高營收品項。
- 天氣欄位可作為短期營收預測與營運規劃的輔助特徵。

---

## 使用技術

- Python
- Pandas
- Power BI
- Streamlit
- Scikit-learn
- XGBoost
- GitHub
- Render

---

## 如何重新產生 Power BI 資料

如果你本機有完整清洗資料：

```text
data/Coffee_Shop_Enterprise_Features_Corrected.csv
```

可以執行：

```bash
python scripts/create_powerbi_data.py
```

執行後會產生：

```text
data/Coffee_Shop_PowerBI_Dashboard_Data.csv
```

---

## 如何執行 Streamlit 專案

如果專案中有 `app.py`，可以執行：

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## GitHub 上傳指令

```bash
git status
git add .
git commit -m "整理咖啡 AI 商業分析專案"
git push
```

---

## 後續優化方向

- 新增 Power BI `.pbix` 檔案
- 新增 Dashboard 截圖到 `screenshots/`
- 新增 Render 線上展示網址
- 新增模型評估結果與預測圖表
- 補上專案簡報 PPT
