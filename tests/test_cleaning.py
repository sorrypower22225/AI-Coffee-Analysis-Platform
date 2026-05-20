import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from config import RAW_DATA_PATH
import pandas as pd

from modules.cleaning import clean_data

df = pd.read_csv(
    RAW_DATA_PATH
)

df = clean_data(df)

print(df.head())

print(df.columns)

print(df.columns)
