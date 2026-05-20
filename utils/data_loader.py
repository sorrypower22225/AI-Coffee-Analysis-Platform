from pathlib import Path
import pandas as pd

from config import DATA_DIR, RAW_DATA_PATH, CLEANED_DATA_PATH, DEMO_DATA_PATH
from utils.schema import ensure_required_columns

# Legacy fallback names only for compatibility if a user manually adds old files back.
LEGACY_RAW_CSV = "Coffee Shop Sales.csv"
RAW_BACKUP_CSV = "Coffee Shop Sales_RAW_BACKUP.csv"
LEGACY_FEATURE_CSV = "Coffee_Shop_Enterprise_Features_Cleaned.csv"


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def data_dir() -> Path:
    return DATA_DIR


def find_data_file(prefer_feature: bool = True, demo: bool = False) -> Path | None:
    """Find the safest built-in CSV.

    prefer_feature=True: use cleaned enterprise feature data for dashboard / AI pages.
    prefer_feature=False: use raw transaction data for validation / re-cleaning flows.
    demo=True: prefer a smaller demo CSV if it exists, useful for online deployment.
    """
    feature_candidates = [CLEANED_DATA_PATH, DATA_DIR / LEGACY_FEATURE_CSV]
    raw_candidates = [RAW_DATA_PATH, DATA_DIR / RAW_BACKUP_CSV, DATA_DIR / LEGACY_RAW_CSV]
    demo_candidates = [DEMO_DATA_PATH]

    if demo:
        candidates = demo_candidates + (feature_candidates if prefer_feature else raw_candidates)
    else:
        candidates = feature_candidates + raw_candidates if prefer_feature else raw_candidates + feature_candidates

    for p in candidates:
        if p.exists():
            return p
    return None


def read_csv_safely(path_or_file, normalize: bool = True):
    try:
        df = pd.read_csv(path_or_file)
    except UnicodeDecodeError:
        df = pd.read_csv(path_or_file, encoding="latin1")
    except Exception:
        df = pd.read_csv(path_or_file, encoding="utf-8-sig")
    # Remove duplicated columns defensively before schema normalization.
    df = df.loc[:, ~df.columns.duplicated()].copy()
    return ensure_required_columns(df) if normalize else df


def load_default_data(prefer_feature: bool = True, demo: bool = False):
    p = find_data_file(prefer_feature=prefer_feature, demo=demo)
    if p is None:
        return None
    return read_csv_safely(p)
