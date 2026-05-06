from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from core import (
    DEFAULT_THRESHOLDS,
    apply_filters,
    get_strategy,
    rules_based_probability,
    score_leads,
    synthetic_demo_portfolio,
    validate_dataset,
    with_derived_fields,
)


def _minimal_valid_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Lead_ID": ["L1", "L2"],
            "Purchase": [0, 1],
            "App_Engagement_Mins": [10.0, 90.0],
            "Web_Configurator_Status": [0, 1],
            "Test_Drive_Completed": [0, 1],
            "Last_Contact_Days": [5, 40],
            "Engagement_Density": [2.0, 1.5],
        }
    )


def test_validate_dataset_ok() -> None:
    assert validate_dataset(_minimal_valid_df()) == []


def test_validate_dataset_missing_columns() -> None:
    df = _minimal_valid_df().drop(columns=["Purchase"])
    issues = validate_dataset(df)
    assert any("Missing required columns" in i for i in issues)


def test_validate_dataset_bad_purchase() -> None:
    df = _minimal_valid_df()
    df.loc[0, "Purchase"] = 2
    issues = validate_dataset(df)
    assert any("non-binary" in i for i in issues)


def test_validate_dataset_null_lead_id() -> None:
    df = _minimal_valid_df()
    df.loc[0, "Lead_ID"] = pd.NA
    issues = validate_dataset(df)
    assert any("nulls" in i for i in issues)


def test_get_strategy_tiers() -> None:
    th = {"vip": 0.85, "hot": 0.60, "nurture": 0.40}
    assert get_strategy(0.90, th) == "VIP Priority"
    assert get_strategy(0.70, th) == "Hot Pipeline"
    assert get_strategy(0.50, th) == "Nurture List"
    assert get_strategy(0.10, th) == "Passive"


def test_rules_based_probability_matches_fallback_scoring(tmp_path: Path) -> None:
    df = synthetic_demo_portfolio(200, seed=1)
    expected = rules_based_probability(df)
    out, status, _ = score_leads(df, tmp_path / "missing.joblib")
    assert status == "rules_fallback"
    pd.testing.assert_series_equal(
        out["Probability"].reset_index(drop=True),
        expected.reset_index(drop=True),
        rtol=1e-12,
        atol=1e-12,
        check_names=False,
    )


def test_synthetic_demo_portfolio_tier_spread(tmp_path: Path) -> None:
    df = synthetic_demo_portfolio(800, seed=3)
    assert len(df) == 800
    assert validate_dataset(df) == []
    pre = rules_based_probability(df)
    assert int((pre >= 0.85).sum()) >= 30
    scored, status, _ = score_leads(df, tmp_path / "missing.joblib")
    assert status == "rules_fallback"
    tiered = with_derived_fields(scored, DEFAULT_THRESHOLDS)
    counts = tiered["Category"].value_counts()
    assert int(counts.get("VIP Priority", 0)) >= 30
    assert int(counts.get("Passive", 0)) >= 100


def test_score_leads_missing_model_artifact(tmp_path: Path) -> None:
    df = _minimal_valid_df()
    out, status, reason = score_leads(df, tmp_path / "nonexistent.joblib")
    assert status == "rules_fallback"
    assert reason is not None
    assert "FileNotFoundError" in reason
    assert "Probability" in out.columns
    assert out["Probability"].between(0, 1).all()


def test_with_derived_fields_and_apply_filters() -> None:
    df = _minimal_valid_df()
    df["Probability"] = [0.9, 0.3]
    out = with_derived_fields(df, DEFAULT_THRESHOLDS)
    assert "Category" in out.columns
    filtered = apply_filters(out, (0.5, 1.0), last_contact_max=180, attrition_only=False)
    assert len(filtered) == 1
    assert float(filtered["Probability"].iloc[0]) == pytest.approx(0.9)


def _load_build_script():
    import importlib.util

    root = Path(__file__).resolve().parent.parent
    path = root / "scripts" / "build_processed_data.py"
    spec = importlib.util.spec_from_file_location("build_processed_data", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_processed_validate_raw_columns() -> None:
    b = _load_build_script()
    bad = pd.DataFrame({"Lead_ID": [1]})
    issues = b.validate_raw_columns(bad)
    assert issues
