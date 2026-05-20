
import inspect
import numpy as np
import pandas as pd

from sklearn.base import clone
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline

from services.features_service import generate_features, build_feature_catalog

try:
    import optuna
except Exception:
    optuna = None

try:
    from xgboost import XGBRegressor
except Exception:
    XGBRegressor = None
try:
    from lightgbm import LGBMRegressor
except Exception:
    LGBMRegressor = None
try:
    from catboost import CatBoostRegressor
except Exception:
    CatBoostRegressor = None

MODELS = {
    "Linear": make_pipeline(StandardScaler(with_mean=False), LinearRegression()),
    "Ridge": make_pipeline(StandardScaler(with_mean=False), Ridge(alpha=1.0)),
    "Lasso": make_pipeline(StandardScaler(with_mean=False), Lasso(alpha=0.0005, max_iter=20000)),
    "RandomForest": RandomForestRegressor(n_estimators=260, random_state=42, n_jobs=-1, min_samples_leaf=1, max_features="sqrt"),
    "ExtraTrees": ExtraTreesRegressor(n_estimators=260, random_state=42, n_jobs=-1, min_samples_leaf=1, max_features="sqrt"),
    "GradientBoosting": GradientBoostingRegressor(n_estimators=220, learning_rate=0.045, max_depth=4, random_state=42),
}
if XGBRegressor is not None:
    MODELS["XGBoost"] = XGBRegressor(n_estimators=260, learning_rate=0.045, max_depth=6, subsample=0.92, colsample_bytree=0.92, random_state=42, eval_metric="rmse", n_jobs=-1)
if LGBMRegressor is not None:
    MODELS["LightGBM"] = LGBMRegressor(n_estimators=300, learning_rate=0.04, num_leaves=48, random_state=42, n_jobs=-1, verbose=-1)
if CatBoostRegressor is not None:
    MODELS["CatBoost"] = CatBoostRegressor(iterations=320, learning_rate=0.045, depth=7, random_state=42, loss_function="RMSE", verbose=0, allow_writing_files=False)

TARGET_COLS = ["total_amount", "Total_Bill"]
RAW_ID_COLS = ["transaction_id"]
DATE_TIME_COLS = ["transaction_date", "transaction_time"]
LEAKAGE_COLS = ["transaction_qty", "unit_price"]
CATBOOST_CATEGORICAL_CANDIDATES = ["store_location", "product_category", "product_type", "product_detail", "size", "Size"]


def _extract_coef_from_pipeline(model):
    if hasattr(model, "named_steps"):
        last = list(model.named_steps.values())[-1]
        if hasattr(last, "coef_"):
            return np.asarray(last.coef_, dtype=float).ravel()
    if hasattr(model, "coef_"):
        return np.asarray(model.coef_, dtype=float).ravel()
    return None


def _supports_catboost_fit(model):
    return CatBoostRegressor is not None and isinstance(model, CatBoostRegressor)


def _clean_feature_matrix(X):
    # 防止上傳 Enterprise CSV 後產生重複欄位，導致 pandas 報：Columns must be same length as key
    X = X.loc[:, ~X.columns.duplicated()].copy()
    for col in X.columns:
        if pd.api.types.is_bool_dtype(X[col]):
            X[col] = X[col].astype(int)
        elif pd.api.types.is_numeric_dtype(X[col]):
            X[col] = pd.to_numeric(X[col], errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)
        else:
            X[col] = X[col].astype(str).fillna("Unknown")
    return X


def _safe_select_top_features(X_all, y, top_n_features):
    """快速且穩定的特徵篩選。大資料只抽樣訓練，避免 Streamlit 卡住。"""
    top_n = int(top_n_features or 0)
    if top_n <= 0 or X_all.shape[1] <= top_n:
        return X_all

    numeric_X = X_all.copy()
    for col in numeric_X.select_dtypes(include=["object", "category"]).columns:
        numeric_X[col] = pd.factorize(numeric_X[col].astype(str), sort=True)[0]
    numeric_X = numeric_X.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)

    # 最多抽樣 15000 筆做特徵重要度，速度穩定很多。
    max_sample = 15000
    if len(numeric_X) > max_sample:
        sample_idx = numeric_X.sample(n=max_sample, random_state=42).index
        fit_X = numeric_X.loc[sample_idx]
        fit_y = pd.Series(y).loc[sample_idx]
    else:
        fit_X = numeric_X
        fit_y = y

    try:
        selector = ExtraTreesRegressor(
            n_estimators=40,
            random_state=42,
            n_jobs=-1,
            min_samples_leaf=2,
            max_features="sqrt",
        )
        selector.fit(fit_X, fit_y)
        imp = pd.Series(selector.feature_importances_, index=numeric_X.columns).sort_values(ascending=False)
        keep = imp.head(top_n).index.tolist()
        return X_all[keep]
    except Exception:
        return X_all.iloc[:, :top_n]


def prepare_model_data(
    df,
    allow_target_leakage=False,
    use_real_weather=True,
    force_refresh_weather=False,
    top_n_features=65,
    model_name=None,
    add_business_aggregates=True,
):
    feature_df = generate_features(
        df,
        use_real_weather=use_real_weather,
        force_refresh_weather=force_refresh_weather,
        add_business_aggregates=add_business_aggregates,
    )
    if "total_amount" not in feature_df.columns:
        raise ValueError("特徵工程後找不到 total_amount 目標欄位。")

    y = pd.to_numeric(feature_df["total_amount"], errors="coerce").fillna(0)
    drop_cols = TARGET_COLS + RAW_ID_COLS + DATE_TIME_COLS
    if not allow_target_leakage:
        drop_cols += LEAKAGE_COLS

    # 安全移除目標欄位與會直接洩漏答案的欄位。
    # Enterprise CSV 有時會因欄位標準化產生 total_amount_1 / total_amount_2 / total_bill 等別名，
    # 若沒有移除，模型會看答案造成 Dashboard 指標異常。
    leak_prefixes = ["total_amount", "total_bill", "Total_Bill"]
    if not allow_target_leakage:
        leak_prefixes += ["transaction_qty", "unit_price"]
    dynamic_drop = []
    for c in feature_df.columns:
        cs = str(c)
        if c in drop_cols:
            dynamic_drop.append(c)
        elif any(cs == p or cs.startswith(p + "_") for p in leak_prefixes):
            dynamic_drop.append(c)

    X_all = feature_df.drop(columns=list(set(dynamic_drop)), errors="ignore")

    # CatBoost 保留原始類別欄位；其他模型使用數值/編碼後特徵。
    use_cat = model_name == "CatBoost" and CatBoostRegressor is not None
    if not use_cat:
        object_cols = X_all.select_dtypes(include=["object", "category", "datetime64[ns]"]).columns.tolist()
        X_all = X_all.drop(columns=object_cols, errors="ignore")
        X_all = X_all.select_dtypes(include=["int64", "float64", "int32", "float32", "bool", "uint32", "uint64"])
    else:
        # 刪掉非候選文字欄位，避免 detail 過長或未知欄位造成雜訊。
        for col in X_all.select_dtypes(include=["object", "category"]).columns:
            if col not in CATBOOST_CATEGORICAL_CANDIDATES:
                X_all = X_all.drop(columns=[col])

    X_all = _clean_feature_matrix(X_all.copy())
    nunique = X_all.nunique(dropna=False)
    X_all = X_all.loc[:, nunique > 1]

    if X_all.empty:
        raise ValueError("沒有可用特徵，請檢查 CSV 欄位與 features_service.py。")
    if len(X_all) < 10:
        raise ValueError("資料筆數不足，至少需要 10 筆以上資料。")

    # 保留最多 TOP N 特徵：使用安全抽樣版，避免大 CSV 卡住或欄位長度錯誤。
    X_all = _safe_select_top_features(X_all, y, top_n_features)

    cat_features = [c for c in CATBOOST_CATEGORICAL_CANDIDATES if c in X_all.columns]
    return X_all, y, cat_features


def get_feature_importance(model):
    if hasattr(model, "feature_importances_"):
        return np.array(model.feature_importances_, dtype=float)
    coef = _extract_coef_from_pipeline(model)
    if coef is not None:
        return np.abs(coef)
    return None


def _fit_model(model, X_train, y_train, cat_features):
    if _supports_catboost_fit(model) and cat_features:
        cat_indices = [X_train.columns.get_loc(c) for c in cat_features if c in X_train.columns]
        model.fit(X_train, y_train, cat_features=cat_indices)
    else:
        # 非 CatBoost 不能吃字串，保險轉數值
        X_fit = X_train.copy()
        for col in X_fit.select_dtypes(include=["object", "category"]).columns:
            X_fit[col] = pd.factorize(X_fit[col].astype(str), sort=True)[0]
        model.fit(X_fit, y_train)
    return model


def _predict_model(model, X_test):
    if _supports_catboost_fit(model):
        return model.predict(X_test)
    Xp = X_test.copy()
    for col in Xp.select_dtypes(include=["object", "category"]).columns:
        Xp[col] = pd.factorize(Xp[col].astype(str), sort=True)[0]
    return model.predict(Xp)


def run_single_model_backtest(
    df,
    model_name,
    random_state=42,
    test_size=0.2,
    allow_target_leakage=False,
    use_real_weather=True,
    force_refresh_weather=False,
    top_n_features=65,
    add_business_aggregates=True,
):
    if model_name not in MODELS:
        raise ValueError(f"找不到模型：{model_name}")

    X, y, cat_features = prepare_model_data(
        df,
        allow_target_leakage=allow_target_leakage,
        use_real_weather=use_real_weather,
        force_refresh_weather=force_refresh_weather,
        top_n_features=top_n_features,
        model_name=model_name,
        add_business_aggregates=add_business_aggregates,
    )
    model = clone(MODELS[model_name])
    if hasattr(model, "random_state"):
        try:
            model.set_params(random_state=random_state)
        except Exception:
            pass

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)

    # 防呆：小樣本或切分後目標值完全相同時，部分模型（尤其 CatBoost）會拒絕訓練。
    # 這裡改用平均值基準預測，確保 Dashboard 不會中斷。
    if pd.Series(y_train).nunique(dropna=False) <= 1:
        y_pred = np.repeat(float(pd.Series(y_train).mean()), len(y_test))
        r2 = 0.0
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        importance = np.zeros(X.shape[1], dtype=float)
    else:
        model = _fit_model(model, X_train, y_train, cat_features)
        y_pred = _predict_model(model, X_test)
        r2 = float(r2_score(y_test, y_pred))
        rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        mae = float(mean_absolute_error(y_test, y_pred))
        importance = get_feature_importance(model)
    if importance is not None:
        importance = np.nan_to_num(importance, nan=0.0, posinf=0.0, neginf=0.0)

    catalog = build_feature_catalog(list(X.columns))
    return {
        "model": model_name,
        "r2": r2,
        "rmse": rmse,
        "mae": mae,
        "feature_importance": importance,
        "features": list(X.columns),
        "feature_catalog": catalog,
        "cat_features": cat_features,
        "n_features": int(X.shape[1]),
        "n_rows": int(X.shape[0]),
    }



def _to_numeric_model_matrix(X):
    """把任何模型矩陣安全轉成純數值，給 Feature Importance / Optuna 使用。"""
    Xn = X.copy()
    for col in Xn.select_dtypes(include=["object", "category", "datetime64[ns]"]).columns:
        Xn[col] = pd.factorize(Xn[col].astype(str), sort=True)[0]
    return Xn.apply(pd.to_numeric, errors="coerce").replace([np.inf, -np.inf], np.nan).fillna(0)


def calculate_global_feature_importance(
    df,
    allow_target_leakage=False,
    use_real_weather=True,
    force_refresh_weather=False,
    add_business_aggregates=True,
    max_sample=20000,
):
    """全域特徵重要性：用全部可用特徵建立一次 ExtraTrees 重要性排序，並標出低貢獻特徵。"""
    X_all, y, _ = prepare_model_data(
        df,
        allow_target_leakage=allow_target_leakage,
        use_real_weather=use_real_weather,
        force_refresh_weather=force_refresh_weather,
        top_n_features=0,   # 0 = 不限制，使用全部可用特徵
        model_name="ExtraTrees",
        add_business_aggregates=add_business_aggregates,
    )
    Xn = _to_numeric_model_matrix(X_all)
    if len(Xn) > max_sample:
        idx = Xn.sample(n=max_sample, random_state=42).index
        fit_X = Xn.loc[idx]
        fit_y = pd.Series(y).loc[idx]
    else:
        fit_X = Xn
        fit_y = y

    selector = ExtraTreesRegressor(
        n_estimators=120,
        random_state=42,
        n_jobs=-1,
        min_samples_leaf=2,
        max_features="sqrt",
    )
    selector.fit(fit_X, fit_y)
    imp = pd.Series(selector.feature_importances_, index=Xn.columns).sort_values(ascending=False)
    out = imp.reset_index()
    out.columns = ["特徵", "重要性"]
    total = float(out["重要性"].sum()) or 1.0
    out["重要性比例"] = out["重要性"] / total
    out["累積重要性"] = out["重要性比例"].cumsum()
    out["排名"] = range(1, len(out) + 1)
    out["建議"] = np.where(
        (out["重要性"] <= 0) | (out["累積重要性"] > 0.98),
        "可考慮移除/觀察",
        "建議保留",
    )
    out = out[["排名", "特徵", "重要性", "重要性比例", "累積重要性", "建議"]]
    useless = out[out["建議"] == "可考慮移除/觀察"].copy()
    keep = out[out["建議"] == "建議保留"].copy()
    return {
        "importance_df": out,
        "keep_features": keep["特徵"].tolist(),
        "useless_features": useless["特徵"].tolist(),
        "n_total_features": int(X_all.shape[1]),
        "n_keep_features": int(len(keep)),
        "n_useless_features": int(len(useless)),
    }


def _build_tuned_model(model_name, params=None, random_state=42):
    """依 Optuna 參數建立模型；沒有參數時回到預設模型。"""
    params = params or {}
    if model_name == "RandomForest":
        return RandomForestRegressor(random_state=random_state, n_jobs=-1, **params)
    if model_name == "ExtraTrees":
        return ExtraTreesRegressor(random_state=random_state, n_jobs=-1, **params)
    if model_name == "GradientBoosting":
        return GradientBoostingRegressor(random_state=random_state, **params)
    if model_name == "XGBoost" and XGBRegressor is not None:
        return XGBRegressor(random_state=random_state, eval_metric="rmse", n_jobs=-1, **params)
    return clone(MODELS[model_name])


def _suggest_model_params(trial, model_name):
    if model_name in ["RandomForest", "ExtraTrees"]:
        return {
            "n_estimators": trial.suggest_int("n_estimators", 80, 360, step=40),
            "max_depth": trial.suggest_int("max_depth", 4, 22),
            "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 8),
            "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", 0.5, 0.8, 1.0]),
        }
    if model_name == "GradientBoosting":
        return {
            "n_estimators": trial.suggest_int("n_estimators", 80, 320, step=40),
            "learning_rate": trial.suggest_float("learning_rate", 0.015, 0.12, log=True),
            "max_depth": trial.suggest_int("max_depth", 2, 6),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
        }
    if model_name == "XGBoost" and XGBRegressor is not None:
        return {
            "n_estimators": trial.suggest_int("n_estimators", 80, 360, step=40),
            "learning_rate": trial.suggest_float("learning_rate", 0.015, 0.12, log=True),
            "max_depth": trial.suggest_int("max_depth", 3, 9),
            "subsample": trial.suggest_float("subsample", 0.65, 1.0),
            "colsample_bytree": trial.suggest_float("colsample_bytree", 0.65, 1.0),
        }
    return {}


def run_optuna_automl_search(
    df,
    n_trials=15,
    allow_target_leakage=False,
    use_real_weather=True,
    force_refresh_weather=False,
    add_business_aggregates=True,
    candidate_models=None,
    random_state=42,
):
    """Optuna AutoML：自動搜尋最佳模型、最佳參數、最佳特徵數。"""
    available = ["RandomForest", "ExtraTrees", "GradientBoosting"]
    if XGBRegressor is not None:
        available.append("XGBoost")
    if candidate_models:
        available = [m for m in candidate_models if m in available]
    if not available:
        raise ValueError("沒有可供 Optuna 搜尋的模型。")

    # 先算一次全部特徵數，讓 Optuna 的特徵數搜尋不會超出範圍。
    X_full, y_full, _ = prepare_model_data(
        df,
        allow_target_leakage=allow_target_leakage,
        use_real_weather=use_real_weather,
        force_refresh_weather=force_refresh_weather,
        top_n_features=0,
        model_name="ExtraTrees",
        add_business_aggregates=add_business_aggregates,
    )
    max_features = int(X_full.shape[1])
    feature_choices = sorted(set([20, 30, 40, 50, 65, 80, 100, 120, max_features]))
    feature_choices = [x for x in feature_choices if 1 <= x <= max_features]

    trial_rows = []

    def objective(trial):
        model_name = trial.suggest_categorical("model", available)
        top_n = trial.suggest_categorical("top_n_features", feature_choices)
        params = _suggest_model_params(trial, model_name)
        X, y, cat_features = prepare_model_data(
            df,
            allow_target_leakage=allow_target_leakage,
            use_real_weather=use_real_weather,
            force_refresh_weather=False,
            top_n_features=top_n,
            model_name=model_name,
            add_business_aggregates=add_business_aggregates,
        )
        Xn = _to_numeric_model_matrix(X)
        X_train, X_test, y_train, y_test = train_test_split(Xn, y, test_size=0.2, random_state=random_state + trial.number)
        if pd.Series(y_train).nunique(dropna=False) <= 1:
            score = -999.0
            rmse = float("inf")
            mae = float("inf")
        else:
            model = _build_tuned_model(model_name, params=params, random_state=random_state + trial.number)
            model.fit(X_train, y_train)
            pred = model.predict(X_test)
            score = float(r2_score(y_test, pred))
            rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
            mae = float(mean_absolute_error(y_test, pred))
        row = {"trial": trial.number + 1, "model": model_name, "top_n_features": top_n, "r2": score, "rmse": rmse, "mae": mae}
        row.update(params)
        trial_rows.append(row)
        return score

    if optuna is not None:
        study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=random_state))
        study.optimize(objective, n_trials=int(n_trials), show_progress_bar=False)
        best_params = dict(study.best_trial.params)
        best_model = best_params.pop("model")
        best_top_n = int(best_params.pop("top_n_features"))
        tuned_model_params = {k: v for k, v in best_params.items()}
    else:
        # 沒安裝 optuna 時仍提供可執行的 AutoML fallback，避免 Streamlit 頁面中斷。
        rng = np.random.default_rng(random_state)
        best_row = None
        for i in range(int(n_trials)):
            class DummyTrial:
                number = i
                def suggest_categorical(self, name, choices):
                    return choices[int(rng.integers(0, len(choices)))]
                def suggest_int(self, name, low, high, step=1):
                    vals = list(range(low, high + 1, step))
                    return vals[int(rng.integers(0, len(vals)))]
                def suggest_float(self, name, low, high, log=False):
                    if log:
                        return float(np.exp(rng.uniform(np.log(low), np.log(high))))
                    return float(rng.uniform(low, high))
            score = objective(DummyTrial())
            if best_row is None or score > best_row.get("r2", -999):
                best_row = dict(trial_rows[-1])
        best_model = best_row.pop("model")
        best_top_n = int(best_row.pop("top_n_features"))
        tuned_model_params = {k: v for k, v in best_row.items() if k not in ["trial", "r2", "rmse", "mae"] and pd.notna(v)}

    X_best, y_best, cat_features = prepare_model_data(
        df,
        allow_target_leakage=allow_target_leakage,
        use_real_weather=use_real_weather,
        force_refresh_weather=False,
        top_n_features=best_top_n,
        model_name=best_model,
        add_business_aggregates=add_business_aggregates,
    )
    Xn_best = _to_numeric_model_matrix(X_best)
    X_train, X_test, y_train, y_test = train_test_split(Xn_best, y_best, test_size=0.2, random_state=random_state)
    final_model = _build_tuned_model(best_model, tuned_model_params, random_state=random_state)
    final_model.fit(X_train, y_train)
    pred = final_model.predict(X_test)
    final_r2 = float(r2_score(y_test, pred))
    final_rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
    final_mae = float(mean_absolute_error(y_test, pred))
    importance = get_feature_importance(final_model)
    if importance is None:
        importance = np.zeros(X_best.shape[1])
    importance = np.nan_to_num(np.asarray(importance, dtype=float), nan=0.0, posinf=0.0, neginf=0.0)
    imp_df = pd.DataFrame({"特徵": list(X_best.columns), "重要性": importance[:len(X_best.columns)]}).sort_values("重要性", ascending=False)
    imp_df.insert(0, "排名", range(1, len(imp_df) + 1))

    trials_df = pd.DataFrame(trial_rows).sort_values("r2", ascending=False).reset_index(drop=True)
    return {
        "best_model": best_model,
        "best_top_n_features": best_top_n,
        "best_params": tuned_model_params,
        "best_r2": final_r2,
        "best_rmse": final_rmse,
        "best_mae": final_mae,
        "best_features": list(X_best.columns),
        "feature_importance_df": imp_df,
        "trials_df": trials_df,
        "n_total_features": max_features,
    }


def calculate_business_accuracy(r2):
    try:
        return max(0, min(100, float(r2) * 100))
    except Exception:
        return 0
