import re
import pandas as pd
import numpy as np

CANONICAL_ALIASES = {
    'transaction_date': ['transaction_date','transaction date','date','datetime','transaction_dt','日期','交易日期'],
    'transaction_time': ['transaction_time','transaction time','time','交易時間','時間'],
    'store_location': ['store_location','store location','store','location','門市','店面','分店','store_name'],
    'store_id': ['store_id','store id','門市id','店號'],
    'product_category': ['product_category','product category','category','商品類別','品類'],
    'product_type': ['product_type','product type','type','商品類型'],
    'product_detail': ['product_detail','product detail','product','item','商品名稱','商品明細'],
    'transaction_qty': ['transaction_qty','transaction qty','qty','quantity','數量','銷量'],
    'unit_price': ['unit_price','unit price','price','單價'],
    # 注意：不要把 total_bill / Total_Bill 在 normalize 階段改名成 total_amount，
    # 否則 ensure_required_columns 重複執行時會產生 duplicated columns。
    'total_amount': ['total_amount','total amount','sales','revenue','amount','營收','金額'],
}

# ensure_required_columns 會建立這些舊版相容欄位。
# normalize_columns 再次執行時必須保留原名，避免 Hour -> hour、Total_Bill -> total_amount 造成重複欄位。
LEGACY_COMPAT_COLUMNS = {'Total_Bill', 'total_bill', 'Hour', 'Month', 'Day', 'Day of Week', 'Size'}

def _key(x: str) -> str:
    x = str(x).replace('\ufeff','').strip().lower()
    x = re.sub(r'[\-\s]+', '_', x)
    x = re.sub(r'[^0-9a-zA-Z_\u4e00-\u9fff]+', '', x)
    x = re.sub(r'_+', '_', x).strip('_')
    return x

ALIAS_TO_CANONICAL = {}
for canonical, aliases in CANONICAL_ALIASES.items():
    for alias in aliases:
        ALIAS_TO_CANONICAL[_key(alias)] = canonical

def make_unique_columns(columns) -> list[str]:
    """Return unique column names while preserving the first occurrence.

    Streamlit / PyArrow cannot render a dataframe when column names are duplicated.
    This helper makes schema normalization idempotent.
    """
    seen = {}
    out = []
    for col in columns:
        base = str(col).replace('\ufeff', '').strip()
        if base == '':
            base = 'unnamed_column'
        if base in seen:
            seen[base] += 1
            out.append(f'{base}__dup{seen[base]}')
        else:
            seen[base] = 0
            out.append(base)
    return out

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize schema while preserving all enterprise feature columns.

    This function is intentionally idempotent: calling it multiple times should not
    create duplicated column names such as hour/hour or total_amount/total_amount.
    """
    if df is None:
        return df
    df = df.copy()
    seen = {}
    new_cols = []
    for col in df.columns:
        original = str(col).replace('\ufeff', '').strip()
        k = _key(original)

        if original in LEGACY_COMPAT_COLUMNS:
            normalized = original
        else:
            normalized = ALIAS_TO_CANONICAL.get(k, k)

        if normalized in seen:
            seen[normalized] += 1
            normalized = f'{normalized}_{seen[normalized]}'
        else:
            seen[normalized] = 0
        new_cols.append(normalized)
    df.columns = make_unique_columns(new_cols)

    # If duplicate normalized columns exist with suffix, merge useful aliases back to canonical when canonical missing.
    for canonical in CANONICAL_ALIASES:
        if canonical not in df.columns:
            candidates = [c for c in df.columns if c.startswith(canonical + '_')]
            if candidates:
                df[canonical] = df[candidates[0]]
    df.columns = make_unique_columns(df.columns)
    return df

def parse_date(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors='coerce')
    s = series.astype(str).str.strip()

    # Maven Coffee Shop Sales uses dd-mm-yyyy, for example 01-06-2023 means
    # 1 June 2023, not January 6. Parse day-first before the generic parser.
    parsed = pd.to_datetime(s, errors='coerce', format='%d-%m-%Y')
    parsed = parsed.fillna(pd.to_datetime(s, errors='coerce', format='%Y-%m-%d'))
    parsed = parsed.fillna(pd.to_datetime(s, errors='coerce', dayfirst=True))
    parsed = parsed.fillna(pd.to_datetime(s, errors='coerce', dayfirst=False))
    return parsed

def parse_time(series: pd.Series) -> pd.Series:
    if pd.api.types.is_datetime64_any_dtype(series):
        return pd.to_datetime(series, errors='coerce')
    s = series.astype(str).str.strip()
    parsed = pd.to_datetime(s, format='%H:%M:%S', errors='coerce')
    missing = parsed.isna()
    if missing.any():
        parsed.loc[missing] = pd.to_datetime(s.loc[missing], format='%H:%M', errors='coerce')
    missing = parsed.isna()
    if missing.any():
        # Some old generated files stored a full datetime in transaction_time.
        # Keep this fallback only for those files.
        parsed.loc[missing] = pd.to_datetime(s.loc[missing], errors='coerce')
    return parsed

def ensure_required_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = normalize_columns(df)

    if 'transaction_date' in df.columns:
        df['transaction_date'] = parse_date(df['transaction_date'])
    else:
        # Last-resort fallback for dashboard stability.
        df['transaction_date'] = pd.date_range('2023-01-01', periods=len(df), freq='D')

    if 'transaction_time' in df.columns:
        df['transaction_time'] = parse_time(df['transaction_time'])
    else:
        hour_source = df['hour'] if 'hour' in df.columns else 0
        hour = pd.to_numeric(hour_source, errors='coerce').fillna(0).clip(0, 23).astype(int)
        df['transaction_time'] = pd.to_datetime(hour.astype(str) + ':00:00', format='%H:%M:%S', errors='coerce')

    if 'total_amount' not in df.columns:
        if 'total_bill' in df.columns:
            df['total_amount'] = pd.to_numeric(df['total_bill'], errors='coerce')
        elif 'Total_Bill' in df.columns:
            df['total_amount'] = pd.to_numeric(df['Total_Bill'], errors='coerce')
        elif 'transaction_qty' in df.columns and 'unit_price' in df.columns:
            df['total_amount'] = pd.to_numeric(df['transaction_qty'], errors='coerce') * pd.to_numeric(df['unit_price'], errors='coerce')
        else:
            df['total_amount'] = 0
    df['total_amount'] = pd.to_numeric(df['total_amount'], errors='coerce')
    df['total_bill'] = df['total_amount']
    df['Total_Bill'] = df['total_amount']  # legacy compatibility

    if 'transaction_qty' not in df.columns:
        df['transaction_qty'] = 1
    df['transaction_qty'] = pd.to_numeric(df['transaction_qty'], errors='coerce').fillna(1)

    if 'unit_price' not in df.columns:
        df['unit_price'] = df['total_amount'] / df['transaction_qty'].replace(0, np.nan)
    df['unit_price'] = pd.to_numeric(df['unit_price'], errors='coerce').fillna(0)

    # friendly categorical defaults
    for col in ['store_location', 'product_category', 'product_type', 'product_detail', 'size']:
        if col not in df.columns:
            df[col] = 'Unknown'
        df[col] = df[col].astype(str).str.strip().replace({'': 'Unknown', 'nan': 'Unknown', 'None': 'Unknown'}).fillna('Unknown')

    # legacy compatibility for feature code that still references capitalized Size
    if 'size' in df.columns and 'Size' not in df.columns:
        df['Size'] = df['size']

    # standard time fields
    df['hour'] = pd.to_numeric(df.get('hour', df['transaction_time'].dt.hour), errors='coerce').fillna(df['transaction_time'].dt.hour).fillna(0).astype(int)
    df['minute'] = pd.to_numeric(df.get('minute', df['transaction_time'].dt.minute), errors='coerce').fillna(df['transaction_time'].dt.minute).fillna(0).astype(int)
    df['month'] = pd.to_numeric(df.get('month', df['transaction_date'].dt.month), errors='coerce').fillna(df['transaction_date'].dt.month).astype(int)
    df['day'] = pd.to_numeric(df.get('day', df['transaction_date'].dt.day), errors='coerce').fillna(df['transaction_date'].dt.day).astype(int)
    df['weekday'] = pd.to_numeric(df.get('weekday', df['transaction_date'].dt.weekday), errors='coerce').fillna(df['transaction_date'].dt.weekday).astype(int)

    # legacy column aliases for older modules
    df['Hour'] = df['hour']
    df['Month'] = df['month']
    df['Day'] = df['day']
    df['Day of Week'] = df['weekday']
    df.columns = make_unique_columns(df.columns)
    return df
