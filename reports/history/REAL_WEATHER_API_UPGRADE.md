# 真實歷史天氣 API 升級說明

本版已將原本的「紐約天氣代理因子」升級為「Open-Meteo 紐約真實歷史天氣 API」。

## 使用來源

- Open-Meteo Historical Weather API
- 免費
- 免 API Key
- 以紐約座標抓取：latitude=40.7128、longitude=-74.0060
- 依交易資料的 transaction_date 自動抓取起訖日期

## 新增天氣欄位

- weather_temp_max_c：每日最高溫，攝氏
- weather_temp_min_c：每日最低溫，攝氏
- weather_temp_mean_c：每日平均溫，攝氏
- weather_precipitation_mm：每日總降水量，毫米
- weather_rain_mm：每日降雨量，毫米
- weather_snowfall_mm：每日降雪量，毫米
- weather_wind_speed_max_kmh：每日最大風速，km/h
- weather_is_real：1 代表真實 API 資料；0 代表備援代理資料
- is_rainy_day：是否下雨
- is_heavy_rain_day：是否大雨
- is_snow_day：是否下雪

## 快取機制

第一次執行會下載天氣資料，並自動存到：

```text
data/weather_cache/
```

之後再次執行會直接讀取快取，不會每次都呼叫 API。

## 安全備援

如果 API 無法連線，例如：

- 電腦沒有網路
- Open-Meteo 暫時無法連線
- Render 部署環境網路異常

系統不會壞掉，會自動改用原本的月度天氣代理因子，並在資料內留下 weather_api_error。

## Streamlit 頁面新增控制

AI 預測頁面新增兩個選項：

1. 使用 Open-Meteo 真實紐約歷史天氣 API
2. 重新下載天氣資料

一般情況只要勾第一個即可。
