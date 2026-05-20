# Power BI DAX 指標

資料表名稱建議使用：`Coffee_Shop_PowerBI_Dashboard_Data`

```DAX
總營收 = SUM('Coffee_Shop_PowerBI_Dashboard_Data'[total_amount])
```

```DAX
總訂單數 = DISTINCTCOUNT('Coffee_Shop_PowerBI_Dashboard_Data'[transaction_id])
```

```DAX
總銷售量 = SUM('Coffee_Shop_PowerBI_Dashboard_Data'[transaction_qty])
```

```DAX
平均客單價 = DIVIDE([總營收], [總訂單數])
```

```DAX
平均商品單價 = AVERAGE('Coffee_Shop_PowerBI_Dashboard_Data'[unit_price])
```

```DAX
尖峰營收 = CALCULATE([總營收], 'Coffee_Shop_PowerBI_Dashboard_Data'[peak_status] = "尖峰")
```

```DAX
離峰營收 = CALCULATE([總營收], 'Coffee_Shop_PowerBI_Dashboard_Data'[peak_status] = "離峰")
```

```DAX
雨天營收 = CALCULATE([總營收], 'Coffee_Shop_PowerBI_Dashboard_Data'[weather_status] = "雨天")
```

```DAX
非雨天營收 = CALCULATE([總營收], 'Coffee_Shop_PowerBI_Dashboard_Data'[weather_status] = "非雨天")
```
