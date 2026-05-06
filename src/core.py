from __future__ import annotations

from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
import streamlit as st


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "apex_leads_final_v3.csv"
MODEL_PATH = BASE_DIR / "models" / "xgb_champion_v3.joblib"


TIER_COLORS = {
    "VIP Priority": "#d9534f",
    "Hot Pipeline": "#f0ad4e",
    "Nurture List": "#5bc0de",
    "Passive": "#94a3b8",
}


DEFAULT_THRESHOLDS = {"vip": 0.85, "hot": 0.60, "nurture": 0.40}


REQUIRED_COLUMNS = {
    "Lead_ID",
    "Purchase",
    "App_Engagement_Mins",
    "Web_Configurator_Status",
    "Test_Drive_Completed",
    "Last_Contact_Days",
    "Engagement_Density",
}


@st.cache_data(ttl=60 * 30, show_spinner=False)
def load_processed_data(path: Path) -> pd.DataFrame:
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def load_model(path: Path) -> Any:
    return joblib.load(path)


def validate_dataset(df: pd.DataFrame) -> list[str]:
    issues: list[str] = []
    missing = sorted(REQUIRED_COLUMNS - set(df.columns))
    if missing:
        issues.append(f"Missing required columns: {', '.join(missing)}")
    if "Purchase" in df.columns:
        bad_purchase = set(pd.Series(df["Purchase"]).dropna().unique()) - {0, 1}
        if bad_purchase:
            issues.append(f"`Purchase` contains non-binary values: {sorted(bad_purchase)}")
    if "Lead_ID" in df.columns and df["Lead_ID"].isna().any():
        issues.append("`Lead_ID` has nulls (expected unique non-null identifiers).")
    return issues


def rules_based_probability(df: pd.DataFrame) -> pd.Series:
    """
    Transparent fallback score in [0, 1].

    Weighted blend of normalized engagement minutes, web-configurator and test-drive
    signals, and engagement density. Used when the trained model artifact is
    unavailable and exposed as a public function so callers (and tests) can
    reproduce the fallback path deterministically.
    """

    def _safe_col(name: str, default: float = 0.0) -> pd.Series:
        if name in df.columns:
            return pd.to_numeric(df[name], errors="coerce").fillna(default)
        return pd.Series([default] * len(df), index=df.index)

    app_mins = _safe_col("App_Engagement_Mins")
    web_cfg = _safe_col("Web_Configurator_Status")
    test_drive = _safe_col("Test_Drive_Completed")
    engagement_density = _safe_col("Engagement_Density")

    raw_score = (
        0.50 * (app_mins / max(app_mins.max(), 1.0))
        + 0.25 * web_cfg.clip(0, 1)
        + 0.20 * test_drive.clip(0, 1)
        + 0.05 * (engagement_density / max(engagement_density.max(), 1.0))
    ).clip(0, 1)

    return raw_score.astype(float)


def synthetic_demo_portfolio(n: int, seed: int = 0) -> pd.DataFrame:
    """
    Build a deterministic synthetic lead portfolio that satisfies validate_dataset
    and produces a realistic spread across all four strategy tiers when scored
    via rules_based_probability + DEFAULT_THRESHOLDS.
    """
    rng = np.random.default_rng(seed)

    # Three behavioural cohorts: high-intent, mid-funnel, and dormant.
    categories = rng.choice(
        ["high", "mid", "low"],
        size=n,
        p=[0.15, 0.30, 0.55],
    )

    app_mins = np.where(
        categories == "high",
        rng.uniform(80.0, 120.0, n),
        np.where(
            categories == "mid",
            rng.uniform(30.0, 80.0, n),
            rng.uniform(1.0, 30.0, n),
        ),
    )

    web_cfg = np.where(
        categories == "high",
        1,
        np.where(categories == "mid", rng.binomial(1, 0.5, n), 0),
    )

    test_drive = np.where(
        categories == "high",
        1,
        np.where(categories == "mid", rng.binomial(1, 0.3, n), 0),
    )

    last_contact = np.where(
        categories == "high",
        rng.integers(0, 10, n),
        np.where(
            categories == "mid",
            rng.integers(5, 30, n),
            rng.integers(20, 90, n),
        ),
    )

    engagement_density = app_mins / (last_contact + 1.0)

    purchase_p = np.where(
        categories == "high",
        0.7,
        np.where(categories == "mid", 0.3, 0.05),
    )
    purchase = rng.binomial(1, purchase_p, n).astype(int)

    lead_ids = [f"DEMO_{i:06d}" for i in range(n)]

    return pd.DataFrame(
        {
            "Lead_ID": lead_ids,
            "Purchase": purchase,
            "App_Engagement_Mins": app_mins.astype(float),
            "Web_Configurator_Status": web_cfg.astype(int),
            "Test_Drive_Completed": test_drive.astype(int),
            "Last_Contact_Days": last_contact.astype(int),
            "Engagement_Density": engagement_density.astype(float),
        }
    )


def score_leads(
    df: pd.DataFrame, model_path: Path
) -> tuple[pd.DataFrame, str, str | None]:
    """
    Attach a Probability column to df.

    - Prefers the saved model artifact when available.
    - Falls back to a transparent rules-based score if model loading/prediction fails.

    Returns ``(df_with_probability, status, reason)`` where ``status`` is either
    ``"model"`` or ``"rules_fallback"`` and ``reason`` is ``None`` on the model
    path or a ``"<ExceptionType>: <message>"`` string when the fallback fires.
    """
    if "Probability" in df.columns and {"Purchase", "Lead_ID"}.issubset(df.columns):
        df = df.copy()
        df = df.drop(columns=["Probability"])

    try:
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {model_path}")

        model = load_model(model_path)
        feature_cols = [c for c in df.columns if c not in {"Purchase", "Lead_ID"}]
        X = df[feature_cols]
        df = df.copy()
        df["Probability"] = model.predict_proba(X)[:, 1]
        return df, "model", None
    except Exception as exc:
        df = df.copy()
        df["Probability"] = rules_based_probability(df)
        reason = f"{type(exc).__name__}: {exc}"
        return df, "rules_fallback", reason


def get_strategy(prob: float, thresholds: dict[str, float]) -> str:
    if prob >= thresholds["vip"]:
        return "VIP Priority"
    if prob >= thresholds["hot"]:
        return "Hot Pipeline"
    if prob >= thresholds["nurture"]:
        return "Nurture List"
    return "Passive"


def decode_one_hot(row: pd.Series, prefix: str) -> str | None:
    cols = [c for c in row.index if c.startswith(prefix)]
    if not cols:
        return None
    best = None
    best_val = -np.inf
    for c in cols:
        val = row.get(c)
        try:
            v = float(val)
        except Exception:
            v = 0.0
        if v > best_val:
            best_val = v
            best = c
    if best is None or best_val <= 0:
        return None
    return best.replace(prefix, "")


def with_derived_fields(df: pd.DataFrame, thresholds: dict[str, float]) -> pd.DataFrame:
    out = df.copy()
    out["Category"] = out["Probability"].apply(lambda p: get_strategy(float(p), thresholds))
    if any(c.startswith("Lead_Source_") for c in out.columns):
        out["Lead_Source"] = out.apply(lambda r: decode_one_hot(r, "Lead_Source_"), axis=1).fillna("Unknown")
    if any(c.startswith("Lead_Temperature_") for c in out.columns):
        out["Lead_Temperature"] = out.apply(lambda r: decode_one_hot(r, "Lead_Temperature_"), axis=1).fillna("Cold")
    return out


def apply_filters(
    df: pd.DataFrame,
    prob_range: tuple[float, float],
    last_contact_max: int,
    attrition_only: bool,
) -> pd.DataFrame:
    out = df.copy()
    out = out[(out["Probability"] >= prob_range[0]) & (out["Probability"] <= prob_range[1])]
    if "Last_Contact_Days" in out.columns:
        out = out[out["Last_Contact_Days"].astype(int) <= int(last_contact_max)]
    if attrition_only and "Attrition_Risk" in out.columns:
        out = out[out["Attrition_Risk"].astype(int) == 1]
    return out

