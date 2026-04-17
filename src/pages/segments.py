from __future__ import annotations

import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt

from viz import apply_exec_dark_style


def main() -> None:
    df_filtered = st.session_state.get("df_filtered")
    tier_colors = st.session_state.get("tier_colors", {})

    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Segment performance (actuals vs predictions)")
    st.caption("Validate strategy tiers using real outcomes (Purchase) and key portfolio drivers.")

    if df_filtered is None or df_filtered.empty:
        st.info("No leads match the current filters.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

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
        sns.barplot(data=g, x="Category", y="purchase_rate", palette=tier_colors, ax=ax)
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
            sns.barplot(data=src, y="Lead_Source", x="leads", color="#d6b36a", ax=ax)
            ax.set_xlabel("Leads")
            ax.set_ylabel("")
            apply_exec_dark_style(ax)
            # For horizontal bars, a vertical grid is more helpful.
            ax.grid(axis="x", linestyle="--", alpha=0.22, color="#94a3b8")
            sns.despine()
            plt.tight_layout()
            st.pyplot(fig, use_container_width=True)
        else:
            st.info("Lead source columns not available in this dataset.")

    st.markdown("</div>", unsafe_allow_html=True)


main()

