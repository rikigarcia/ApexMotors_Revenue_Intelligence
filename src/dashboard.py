from __future__ import annotations

from contextlib import suppress

import streamlit as st


st.set_page_config(page_title="ApexMotors Command Center", page_icon="🏁", layout="wide")

st.info(
    "This project has been upgraded to a multi-page production app.\n\n"
    "Run the new entrypoint:\n"
    "- `streamlit run src/app.py`",
    icon="ℹ️",
)

with suppress(Exception):
    st.switch_page("app.py")

# --- PATH INITIALIZATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "apex_leads_final_v3.csv"
MODEL_PATH = BASE_DIR / "models" / "xgb_champion_v3.joblib"

TIER_COLORS = {
    "VIP Priority": "#d9534f",
    "Hot Pipeline": "#f0ad4e",
    "Nurture List": "#5bc0de",
    "Passive": "#94a3b8",
}

DEFAULT_THRESHOLDS = {
    "vip": 0.85,
    "hot": 0.60,
    "nurture": 0.40,
}

REQUIRED_COLUMNS = {
    "Lead_ID",
    "Purchase",
    "App_Engagement_Mins",
    "Web_Configurator_Status",
    "Test_Drive_Completed",
    "Last_Contact_Days",
    "Engagement_Density",
}


# --- DATA LOADING / VALIDATION ---
@st.cache_data(ttl=60 * 30, show_spinner=False)
def load_processed_data(path: Path) -> pd.DataFrame:
    """Load the repository's processed feature dataset."""
    return pd.read_csv(path)


@st.cache_resource(show_spinner=False)
def load_model(path: Path):
    """Load the serialized model artifact if available."""
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


def score_leads(df: pd.DataFrame, model_path: Path) -> tuple[pd.DataFrame, str]:
    """
    Attach a Probability column to df.

    - Prefers the saved model artifact when available.
    - Falls back to a transparent rules-based score if model loading/prediction fails.
    """
    if "Probability" in df.columns and {"Purchase", "Lead_ID"}.issubset(df.columns):
        df = df.copy()
        df = df.drop(columns=["Probability"])

    model_status = "rules_fallback"
    try:
        if not model_path.exists():
            raise FileNotFoundError(f"Model artifact not found at {model_path}")

        model = load_model(model_path)
        feature_cols = [c for c in df.columns if c not in {"Purchase", "Lead_ID"}]
        X = df[feature_cols]
        df = df.copy()
        df["Probability"] = model.predict_proba(X)[:, 1]
        model_status = "model"
        return df, model_status
    except Exception:
        df = df.copy()

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

        df["Probability"] = raw_score.astype(float)
        return df, model_status

def get_strategy(prob: float, thresholds: dict[str, float]) -> str:
    """Assign leads to the Marketing Automation Matrix tiers."""
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
    # Best-effort decoding (works with one-hot columns present in the processed dataset)
    if any(c.startswith("Lead_Source_") for c in out.columns):
        out["Lead_Source"] = out.apply(lambda r: decode_one_hot(r, "Lead_Source_"), axis=1).fillna("Unknown")
    if any(c.startswith("Lead_Temperature_") for c in out.columns):
        out["Lead_Temperature"] = (
            out.apply(lambda r: decode_one_hot(r, "Lead_Temperature_"), axis=1).fillna("Cold")
        )
    return out

# --- APP HEADER (TOP BAR) ---
topbar()

with st.sidebar:
    st.markdown("## Command Center")
    st.caption("Controls and runtime info.")

    demo_mode = st.toggle("Demo mode (synthetic leads)", value=False, help="Use synthetic leads if the processed CSV is missing.")
    st.divider()

    st.markdown("### Tier thresholds")
    vip_th = st.slider("VIP Priority ≥", 0.50, 0.99, float(DEFAULT_THRESHOLDS["vip"]), 0.01)
    hot_th = st.slider("Hot Pipeline ≥", 0.20, min(0.95, vip_th - 0.01), float(DEFAULT_THRESHOLDS["hot"]), 0.01)
    nurture_th = st.slider("Nurture List ≥", 0.05, min(0.90, hot_th - 0.01), float(DEFAULT_THRESHOLDS["nurture"]), 0.01)
    thresholds = {"vip": vip_th, "hot": hot_th, "nurture": nurture_th}

    st.divider()
    st.markdown("### Portfolio filters")
    prob_range = st.slider("Probability range", 0.0, 1.0, (0.0, 1.0), 0.01)
    last_contact_max = st.slider("Last contact (days) ≤", 0, 180, 180, 1)
    include_attrition_only = st.toggle("Only attrition-risk leads", value=False, help="Keeps only Attrition_Risk == 1 when available.")

    st.divider()
    st.markdown("### Runtime status")
    st.code(str(DATA_PATH), language="text")
    st.code(str(MODEL_PATH), language="text")

if not DATA_PATH.exists():
    if demo_mode:
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
            }
        )
        st.warning(
            "Demo mode is ON. Displayed leads are synthetic (not from repository data).",
            icon="⚠️",
        )
    else:
        st.error(
            f"Processed dataset not found at `{DATA_PATH}`. "
            "Run the data-prep step to generate it, or enable Demo mode in the sidebar."
        )
        st.stop()
else:
    df = load_processed_data(DATA_PATH)

issues = validate_dataset(df)
if issues:
    st.error("Dataset validation failed. Fix the processed dataset before using the dashboard.")
    for msg in issues:
        st.write(f"- {msg}")
    st.stop()

df, model_status = score_leads(df, MODEL_PATH)
with st.sidebar:
    st.markdown("### Scoring")
    if model_status == "model":
        st.success("Using model artifact")
    else:
        st.warning("Rules-based fallback", icon="⚠️")
    st.caption("Tip (macOS): install `libomp` to load XGBoost artifacts reliably.")

df = with_derived_fields(df, thresholds)

# Apply sidebar filters (portfolio-wide)
df_filtered = df.copy()
df_filtered = df_filtered[(df_filtered["Probability"] >= prob_range[0]) & (df_filtered["Probability"] <= prob_range[1])]
if "Last_Contact_Days" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Last_Contact_Days"].astype(int) <= int(last_contact_max)]
if include_attrition_only and "Attrition_Risk" in df_filtered.columns:
    df_filtered = df_filtered[df_filtered["Attrition_Risk"].astype(int) == 1]

tabs = st.tabs(["Overview", "Segments", "Lead Explorer", "Strategy"])

with tabs[0]:
    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Portfolio KPIs")

    if df_filtered.empty:
        st.info("No leads match the current filters. Expand filters in the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        total = len(df_filtered)
        vip_count = int((df_filtered["Category"] == "VIP Priority").sum())
        hot_count = int((df_filtered["Category"] == "Hot Pipeline").sum())
        nurture_count = int((df_filtered["Category"] == "Nurture List").sum())
        avg_prob = float(df_filtered["Probability"].mean()) * 100.0
        actual_rate = float(df_filtered["Purchase"].mean()) * 100.0 if "Purchase" in df_filtered.columns else np.nan

        k1, k2, k3, k4, k5 = st.columns(5, gap="medium")
        with k1:
            kpi_card("Leads (filtered)", f"{total:,}", "Active portfolio", "total")
        with k2:
            kpi_card("VIP Priority", f"{vip_count:,}", f"{vip_count/max(total,1)*100:.1f}% of filtered", "vip")
        with k3:
            kpi_card("Hot Pipeline", f"{hot_count:,}", f"{hot_count/max(total,1)*100:.1f}% of filtered", "hot")
        with k4:
            kpi_card("Nurture List", f"{nurture_count:,}", f"{nurture_count/max(total,1)*100:.1f}% of filtered", "nurture")
        with k5:
            kpi_card("Portfolio health", f"{avg_prob:.1f}%", f"Actual rate: {actual_rate:.1f}%", "health")

        st.markdown("<br/>", unsafe_allow_html=True)
        left_col, right_col = st.columns([1.15, 0.85], gap="large")

        with left_col:
            st.markdown("#### Lead volume by tier")
            fig, ax = plt.subplots(figsize=(10, 5.5))
            sns.countplot(
                data=df_filtered,
                x="Category",
                palette=TIER_COLORS,
                order=["VIP Priority", "Hot Pipeline", "Nurture List", "Passive"],
                ax=ax,
            )
            ax.set_ylabel("Lead count")
            ax.set_xlabel("")
            apply_exec_dark_style(ax)
            sns.despine()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        with right_col:
            st.markdown("#### Portfolio health")
            fig2, ax2 = plt.subplots(figsize=(8, 5.5))
            sns.histplot(
                data=df_filtered,
                x="Probability",
                hue="Category",
                bins=24,
                element="step",
                stat="count",
                palette=TIER_COLORS,
                ax=ax2,
            )
            ax2.set_xlabel("Predicted purchase probability")
            ax2.set_ylabel("Lead count")
            apply_exec_dark_style(ax2)
            sns.despine()
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=True)

        st.markdown("<br/>", unsafe_allow_html=True)
        st.markdown("#### Alerts & next actions")
        a1, a2, a3 = st.columns([1, 1, 1], gap="large")
        with a1:
            overdue = int((df_filtered["Last_Contact_Days"] >= 30).sum()) if "Last_Contact_Days" in df_filtered.columns else 0
            st.markdown("**Overdue contacts (≥30 days)**")
            st.write(f"{overdue:,} leads need follow-up.")
        with a2:
            if "Attrition_Risk" in df_filtered.columns:
                at_risk = int((df_filtered["Attrition_Risk"] == 1).sum())
                st.markdown("**Attrition risk flagged**")
                st.write(f"{at_risk:,} leads flagged as at-risk.")
            else:
                st.markdown("**Attrition risk flagged**")
                st.write("Attrition_Risk not available.")
        with a3:
            top_vip = df_filtered[df_filtered["Category"] == "VIP Priority"].sort_values("Probability", ascending=False).head(5)
            st.markdown("**Top VIP leads**")
            if top_vip.empty:
                st.write("No VIP leads under current filters.")
            else:
                st.dataframe(
                    top_vip[["Lead_ID", "Probability", "Last_Contact_Days"] if "Last_Contact_Days" in top_vip.columns else ["Lead_ID", "Probability"]],
                    use_container_width=True,
                    hide_index=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

with tabs[1]:
    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Segment performance (actuals vs predictions)")
    if df_filtered.empty:
        st.info("No leads match the current filters.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        g = (
            df_filtered.groupby("Category", dropna=False)
            .agg(
                leads=("Lead_ID", "count"),
                avg_prob=("Probability", "mean"),
                purchase_rate=("Purchase", "mean"),
                avg_last_contact=("Last_Contact_Days", "mean"),
            )
            .reindex(["VIP Priority", "Hot Pipeline", "Nurture List", "Passive"])
            .reset_index()
        )
        g["avg_prob"] = (g["avg_prob"] * 100.0).round(1)
        g["purchase_rate"] = (g["purchase_rate"] * 100.0).round(1)
        g["avg_last_contact"] = g["avg_last_contact"].round(1)

        st.dataframe(
            g,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": st.column_config.TextColumn("Tier"),
                "leads": st.column_config.NumberColumn("Leads"),
                "avg_prob": st.column_config.NumberColumn("Avg probability (%)"),
                "purchase_rate": st.column_config.NumberColumn("Actual purchase rate (%)"),
                "avg_last_contact": st.column_config.NumberColumn("Avg last contact (days)"),
            },
        )

        seg_left, seg_right = st.columns([1, 1], gap="large")
        with seg_left:
            st.markdown("#### Actual purchase rate by tier")
            fig, ax = plt.subplots(figsize=(10, 5.2))
            sns.barplot(data=g, x="Category", y="purchase_rate", palette=TIER_COLORS, ax=ax)
            ax.set_ylabel("Purchase rate (%)")
            ax.set_xlabel("")
            apply_exec_dark_style(ax)
            sns.despine()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)

        with seg_right:
            if "Lead_Source" in df_filtered.columns:
                st.markdown("#### Lead sources (mix)")
                src = (
                    df_filtered.groupby("Lead_Source", dropna=False)
                    .size()
                    .sort_values(ascending=False)
                    .head(10)
                    .reset_index(name="leads")
                )
                fig, ax = plt.subplots(figsize=(10, 5.2))
                sns.barplot(data=src, y="Lead_Source", x="leads", color="#1e293b", ax=ax)
                ax.set_xlabel("Leads")
                ax.set_ylabel("")
                apply_exec_dark_style(ax)
                ax.grid(axis="x", linestyle="--", alpha=0.22, color="#94a3b8")
                sns.despine()
                plt.tight_layout()
                st.pyplot(fig, use_container_width=True)
            else:
                st.info("Lead source columns not available in this dataset.")

        st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Lead explorer + CRM export")
    if df_filtered.empty:
        st.info("No leads match the current filters.")
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        explorer_cols = ["Lead_ID", "Category", "Probability", "Purchase"]
        for extra in ["Lead_Source", "Lead_Temperature", "Last_Contact_Days", "Attrition_Risk", "High_Intent_Signal"]:
            if extra in df_filtered.columns:
                explorer_cols.append(extra)

        search = st.text_input("Search Lead_ID", value="", placeholder="e.g., 75efda40")
        view = df_filtered.copy()
        if search.strip():
            view = view[view["Lead_ID"].astype(str).str.contains(search.strip(), case=False, na=False)]

        view = view.sort_values(by="Probability", ascending=False)

        st.dataframe(
            view[explorer_cols],
            use_container_width=True,
            hide_index=True,
            column_config={
                "Probability": st.column_config.ProgressColumn(
                    "Probability",
                    format="%.3f",
                    min_value=0.0,
                    max_value=1.0,
                )
            },
        )

        st.markdown("#### Export")
        export_cat = st.multiselect(
            "Include tiers",
            options=["VIP Priority", "Hot Pipeline", "Nurture List", "Passive"],
            default=["VIP Priority", "Hot Pipeline", "Nurture List"],
        )
        export_df = view[view["Category"].isin(export_cat)].copy()
        export_payload_cols = ["Lead_ID", "Category", "Probability"]
        if "Lead_Source" in export_df.columns:
            export_payload_cols.append("Lead_Source")
        if "Lead_Temperature" in export_df.columns:
            export_payload_cols.append("Lead_Temperature")
        if "Last_Contact_Days" in export_df.columns:
            export_payload_cols.append("Last_Contact_Days")
        if "Attrition_Risk" in export_df.columns:
            export_payload_cols.append("Attrition_Risk")

        csv_bytes = export_df[export_payload_cols].to_csv(index=False).encode("utf-8")
        st.download_button(
            label="Download filtered CSV",
            data=csv_bytes,
            file_name="apexmotors_filtered_leads.csv",
            mime="text/csv",
            use_container_width=True,
        )
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[3]:
    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Automation matrix & strategic logic")
    st.markdown(
        f"""
The **Apex Automation Matrix** assigns each lead to an automated workflow based on the predicted probability:

- **VIP Priority (≥ {thresholds['vip']:.0%})**: immediate alert to sales manager; concierge outreach; premium preview invite.
- **Hot Pipeline (≥ {thresholds['hot']:.0%})**: 24-hour callback SLA; retargeting based on configuration signals.
- **Nurture List (≥ {thresholds['nurture']:.0%})**: multi-touch education drip; progressive profiling.
- **Passive (< {thresholds['nurture']:.0%})**: brand-only cadence to minimize operational cost.
        """
    )

    with st.expander("Model/runtime notes"):
        st.write(
            "- If the XGBoost artifact can’t load, scoring falls back to a rules-based method for transparency.\n"
            "- On macOS, install `libomp` if you want to load the saved model artifact."
        )
    st.markdown("</div>", unsafe_allow_html=True)

st.caption("ApexMotors Revenue Intelligence v3.0 | Command Center | 2026")