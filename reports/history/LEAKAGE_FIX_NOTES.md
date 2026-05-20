# AI 預測模型資料洩漏修正版

本版已修正：

- 強制移除 `Total_Bill` / `total_amount`，避免模型直接看到答案。
- train/test 改成時間序列切分：`shuffle=False`。
- 訓練前依 `transaction_date` / `transaction_time` 排序。
- 新增資料洩漏檢查：檢查 `Total_Bill`、`total_amount`、`future`、`target` 等欄位是否進入模型。
- 新增 Train R² / Test R² / 過擬合差距。
- 移除同日答案衍生欄位 `store_high_sales_day`。
- 保留可選交易金額解釋模式：可使用 `transaction_qty` 與 `unit_price`，但仍不允許 `Total_Bill` 進入模型。

## 使用建議

正式事前銷售預測：不要勾選 `使用 transaction_qty 與 unit_price`。

交易明細金額解釋：可以勾選 `使用 transaction_qty 與 unit_price`，分數會較高，但這比較像解釋交易金額，不是未來營收預測。
