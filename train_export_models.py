from config import RAW_DATA_PATH
import os
import pandas as pd

from services.forecasting_service import train_test_export_models


DATA_PATH = RAW_DATA_PATH
OUTPUT_DIR = os.path.join("models", "exported_latest")


def main():
    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"找不到資料檔：{DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    result = train_test_export_models(
        df=df,
        output_dir=OUTPUT_DIR,
        test_size=0.2,
        allow_target_leakage=True,
        use_real_weather=True,
        force_refresh_weather=False,
        feature_mode="optimized",
        random_state=42,
    )

    print("✅ 一鍵訓練 + 測試 + 匯出完成")
    print(f"最佳模型：{result['best_model']}")
    print(f"最佳模型檔案：{result['best_model_path']}")
    print(f"全部模型 ZIP：{result['zip_path']}")
    print("\n排行榜：")
    print(result["leaderboard"].to_string(index=False))


if __name__ == "__main__":
    main()
