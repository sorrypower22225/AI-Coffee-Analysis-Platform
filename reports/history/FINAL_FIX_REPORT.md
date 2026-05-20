# AI Coffee Ultimate 最終可執行版修正報告

## 已修正重點

1. **移除重複專案結構**
   - 原 ZIP 內同時存在外層與內層 `AI_Coffee_Ultimate_FINAL_FIXED_V2`，容易執行到錯誤版本。
   - 最終版只保留一份乾淨專案。

2. **修正資料讀取優先順序**
   - 原本系統優先讀取 `Coffee_Shop_Enterprise_Features_Cleaned.csv`。
   - 該檔案內日期、月份、交易時間已有加工錯誤風險。
   - 最終版改成優先讀取 `data/Coffee Shop Sales_RAW_BACKUP.csv`。

3. **修正日期解析**
   - Maven Coffee Shop Sales 原始日期格式是 `dd-mm-yyyy`。
   - 例如 `01-06-2023` 應為 2023-06-01，不是 2023-01-06。
   - 已在 `utils/schema.py` 修正為 day-first 解析。

4. **修正主資料檔**
   - `data/Coffee Shop Sales.csv` 已替換為原始 18 欄版本。
   - 移除錯誤加工後的大型 enterprise CSV，避免系統誤讀。

5. **requirements 補齊**
   - 補上 `sqlalchemy`。
   - 保留 Streamlit、Plotly、Scikit-learn、XGBoost、LightGBM、CatBoost、Optuna 等必要套件。

6. **語法檢查通過**
   - 已對所有 `.py` 檔執行 Python 語法編譯檢查。
   - 結果：0 個語法錯誤。

## 目前資料檢查結果

- 交易筆數：149,116 筆
- 欄位數：27 欄，包含標準化欄位
- 日期範圍：2023-01-01 到 2023-06-30
- transaction_qty 不再全部是 1，包含 1、2、3、4、6、8
- 金額公式 `transaction_qty × unit_price = total_amount` 檢查正常

## 啟動方式

Windows：

```bat
cd AI_Coffee_Ultimate_FINAL_EXECUTABLE
pip install -r requirements.txt
streamlit run app.py
```

或直接雙擊：

```bat
run_app.bat
```

## 建議

- 這份資料是 Maven Analytics 的 fictitious coffee shop 範例資料，報告中請說明為「虛構咖啡店交易資料」。
- 若要正式放 GitHub 或 Render，建議不要上傳大型錯誤加工 CSV，只保留原始 CSV 與程式自動產生特徵。
