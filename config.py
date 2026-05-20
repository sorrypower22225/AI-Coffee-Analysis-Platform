"""Central project configuration for AI Coffee Portfolio Final."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
REPORTS_DIR = BASE_DIR / "reports"
MODELS_DIR = BASE_DIR / "models"

RAW_DATA_FILENAME = "Coffee Shop Sales_RAW.csv"
CLEANED_DATA_FILENAME = "Coffee_Shop_Enterprise_Features_Corrected.csv"
LOCATION_DATA_FILENAME = "location_data.csv"
DEMO_DATA_FILENAME = "Coffee_Shop_Demo.csv"

RAW_DATA_PATH = DATA_DIR / RAW_DATA_FILENAME
CLEANED_DATA_PATH = DATA_DIR / CLEANED_DATA_FILENAME
LOCATION_DATA_PATH = DATA_DIR / LOCATION_DATA_FILENAME
DEMO_DATA_PATH = DATA_DIR / DEMO_DATA_FILENAME

# App defaults
DEFAULT_USE_CLEANED_DATA = True
APP_TITLE = "AI 咖啡營運分析平台"
