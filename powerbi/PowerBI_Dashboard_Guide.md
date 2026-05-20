# Power BI Dashboard 製作指南

請匯入：

```text
data/Coffee_Shop_PowerBI_Dashboard_Data.csv
```

## 第 1 頁：營運總覽

建議圖表：

- 卡片：總營收
- 卡片：總訂單數
- 卡片：總銷售量
- 卡片：平均客單價
- 折線圖：transaction_date / month_name vs 總營收
- 長條圖：store_location vs 總營收
- 長條圖或甜甜圈圖：product_category vs 總營收

## 第 2 頁：店鋪績效分析

建議圖表：

- 長條圖：store_location vs 總營收
- 長條圖：store_location vs 總訂單數
- 長條圖：store_location vs 總銷售量
- 矩陣：store_location、總營收、總訂單數、總銷售量、平均客單價

## 第 3 頁：商品銷售分析

建議圖表：

- 長條圖：product_detail vs 總營收，篩選 Top 10
- 長條圖：product_category vs 總營收
- 長條圖：product_type vs 總銷售量
- 表格：product_detail、總營收、總銷售量、平均商品單價

## 第 4 頁：尖峰離峰分析

建議圖表：

- 折線圖：hour vs 總營收
- 折線圖：hour vs 總訂單數
- 長條圖：peak_status vs 總營收
- 矩陣：day_name、hour、總營收

## 第 5 頁：天氣與營收影響

建議圖表：

- 長條圖：weather_status vs 總營收
- 散佈圖：weather_temp_mean_c vs total_amount
- 散佈圖：weather_precipitation_mm vs total_amount
- 表格：weather_status、總營收、總訂單數、平均客單價
