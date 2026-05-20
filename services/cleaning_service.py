import pandas as pd
import numpy as np
from utils.schema import normalize_columns, ensure_required_columns


def _dedupe_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Remove duplicated column names safely, keeping the first occurrence."""
    if df is None:
        return df
    df = df.copy()
    df.columns = [str(c).strip() for c in df.columns]
    return df.loc[:, ~pd.Index(df.columns).duplicated()].copy()


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """全平台共用資料清洗引擎：支援原始 CSV 與 Enterprise Feature CSV。"""
    if df is None or df.empty:
        raise ValueError('資料為空，請確認 CSV 是否正確上傳。')

    df = _dedupe_columns(df)
    df = ensure_required_columns(df)
    df = _dedupe_columns(df)

    # remove invalid essential rows only
    df['transaction_date'] = pd.to_datetime(df['transaction_date'], errors='coerce')
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    df = df.dropna(subset=['transaction_date', 'total_amount'])
    df = df[df['total_amount'] > 0]
    df = df.replace([np.inf, -np.inf], np.nan)

    # fill numeric missing values column-by-column to avoid duplicated-column assignment errors
    for col in df.select_dtypes(include=[np.number, 'bool']).columns.tolist():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    for col in df.select_dtypes(include=['object', 'category']).columns.tolist():
        if col in df.columns:
            df[col] = df[col].astype(str).fillna('Unknown')

    return df.reset_index(drop=True)


# backward-compatible name used by older code
def normalize_schema(df: pd.DataFrame) -> pd.DataFrame:
    return normalize_columns(df)
