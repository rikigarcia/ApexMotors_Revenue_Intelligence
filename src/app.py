from __future__ import annotations

import numpy as np
import pandas as pd
import streamlit as st

from core import (
    DATA_PATH,
    MODEL_PATH,
    DEFAULT_THRESHOLDS,
    TIER_COLORS,
    apply_filters,
    load_processed_data,
    score_leads,
    validate_dataset,
    with_derived_fields,
)
from styles import inject_global_css
from ui_components import topbar


def ensure_state() -> None:
    st.session_state.setdefault("demo_mode", False)
    st.session_state.setdefault("vip_th", float(DEFAULT_THRESHOLDS["vip"]))
    st.session_state.setdefault("hot_th", float(DEFAULT_THRESHOLDS["hot"]))
    st.session_state.setdefault("nurture_th", float(DEFAULT_THRESHOLDS["nurture"]))
    st.session_state.setdefault("prob_min", 0.0)
    st.session_state.setdefault("prob_max", 1.0)
    st.session_state.setdefault("last_contact_max", 180)
    st.session_state.setdefault("attrition_only", False)


def render_sidebar(model_status: str | None) -> dict[str, object]:
    with st.sidebar:
        st.markdown("## Command Center")
        st.caption("Filters, thresholds, and runtime status.")

        st.toggle("Demo mode (synthetic leads)", key="demo_mode")
        st.divider()

        st.markdown("### Tier thresholds")
        vip_th = st.slider("VIP Priority ≥", 0.50, 0.99, key="vip_th", step=0.01)
        hot_max = min(0.95, float(vip_th) - 0.01)
        hot_th = st.slider("Hot Pipeline ≥", 0.20, hot_max, key="hot_th", step=0.01)
        nurture_max = min(0.90, float(hot_th) - 0.01)
        nurture_th = st.slider("Nurture List ≥", 0.05, nurture_max, key="nurture_th", step=0.01)

        st.divider()
        st.markdown("### Portfolio filters")
        prob_min, prob_max = st.slider("Probability range", 0.0, 1.0, (st.session_state["prob_min"], st.session_state["prob_max"]), 0.01)
        st.session_state["prob_min"] = float(prob_min)
        st.session_state["prob_max"] = float(prob_max)
        st.slider("Last contact (days) ≤", 0, 180, key="last_contact_max", step=1)
        st.toggle("Only attrition-risk leads", key="attrition_only")

        st.divider()
        st.markdown("### Scoring")
        if model_status == "model":
            st.success("Using model artifact")
        elif model_status is not None:
            st.warning("Rules-based fallback", icon="⚠️")
        st.caption("macOS tip: install `libomp` to load XGBoost artifacts reliably.")

        st.divider()
        st.markdown("### Runtime status")
        st.code(str(DATA_PATH), language="text")
        st.code(str(MODEL_PATH), language="text")

    thresholds = {"vip": float(vip_th), "hot": float(hot_th), "nurture": float(nurture_th)}
    filters = {
        "prob_range": (float(st.session_state["prob_min"]), float(st.session_state["prob_max"])),
        "last_contact_max": int(st.session_state["last_contact_max"]),
        "attrition_only": bool(st.session_state["attrition_only"]),
    }
    return {"thresholds": thresholds, "filters": filters}


def prompt_demo_if_missing_processed_file() -> None:
    """
    First-run UX: if the processed CSV is absent, show a clear path forward *before*
    st.stop() — otherwise users never reach the sidebar Demo toggle.
    """
    if DATA_PATH.exists():
        return
    if st.session_state.get("demo_mode", False):
        return

    st.warning("No processed dataset found on disk.")
    st.info(
        f"**Expected file:** `{DATA_PATH}`\n\n"
        "**Option A — try the app now:** turn on **Demo mode** below (same control as in the sidebar). "
        "No CSV or model files are required.\n\n"
        "**Option B — use your own data:** add the processed CSV at that path, or run "
        "`python scripts/build_processed_data.py` after you have a raw extract in `data/raw/` "
        "(see README Quick start)."
    )
    st.toggle(
        "Demo mode (synthetic leads)",
        key="demo_mode",
        help="Generates a small synthetic portfolio so you can explore the Command Center immediately.",
    )
    st.stop()


def get_dataset() -> tuple[pd.DataFrame, str | None]:
    if not DATA_PATH.exists():
        if st.session_state.get("demo_mode", False):
            np.random.seed(42)
            df = pd.DataFrame(
                {
                    "Lead_ID": [f"DEMO_{i}" for i in range(1000, 1307)],
                    "App_Engagement_Mins": np.random.uniform(1, 120, 307),
                    "Web_Configurator_Status": np.random.choice([0, 1], 307, p=[0.6, 0.4]),
                    "Test_Drive_Completed": np.random.choice([0, 1], 307, p=[0.7, 0.3]),
                    "Last_Contact_Days": np.random.randint(0, 90, 307),
                    "Engagement_Density": np.random.uniform(0, 5, 307),
                    "High_Intent_Signal": np.random.choice([0, 1], 307, p=[0.75, 0.25]),
                    "Attrition_Risk": np.random.choice([0, 1], 307, p=[0.7, 0.3]),
                    "Purchase": np.random.choice([0, 1], 307, p=[0.83, 0.17]),
                }
            )
            return df, None
        # Should be unreachable if prompt_demo_if_missing_processed_file() ran first.
        st.error(f"Processed dataset not found at `{DATA_PATH}`. Enable Demo mode or add the file.")
        st.stop()
    return load_processed_data(DATA_PATH), None


def main() -> None:
    st.set_page_config(
        page_title="ApexMotors Command Center",
        page_icon="🏁",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    inject_global_css()
    ensure_state()
    topbar()
    prompt_demo_if_missing_processed_file()

    df, _ = get_dataset()
    issues = validate_dataset(df)
    if issues:
        st.error("Dataset validation failed. Fix the processed dataset before using the dashboard.")
        for msg in issues:
            st.write(f"- {msg}")
        st.stop()

    df_scored, model_status = score_leads(df, MODEL_PATH)
    ctx = render_sidebar(model_status)

    thresholds = ctx["thresholds"]
    filters = ctx["filters"]

    df_scored = with_derived_fields(df_scored, thresholds)
    df_filtered = apply_filters(df_scored, filters["prob_range"], filters["last_contact_max"], filters["attrition_only"])

    st.session_state["df_scored"] = df_scored
    st.session_state["df_filtered"] = df_filtered
    st.session_state["tier_colors"] = TIER_COLORS

    pages = [
        st.Page("pages/overview.py", title="Overview", icon="📈"),
        st.Page("pages/segments.py", title="Segments", icon="🧩"),
        st.Page("pages/explorer.py", title="Lead Explorer", icon="🔎"),
        st.Page("pages/strategy.py", title="Strategy", icon="🧠"),
    ]
    nav = st.navigation(pages)
    nav.run()


if __name__ == "__main__":
    main()

