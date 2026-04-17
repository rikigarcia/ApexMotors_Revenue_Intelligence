from __future__ import annotations

import numpy as np
import seaborn as sns
import streamlit as st
from matplotlib import pyplot as plt

from ui_components import kpi_card
from viz import apply_exec_dark_style
from reporting import ExecutiveSnapshot, build_executive_snapshot_pdf, now_iso_local


def main() -> None:
    df_filtered = st.session_state.get("df_filtered")
    df_scored = st.session_state.get("df_scored")
    tier_colors = st.session_state.get("tier_colors", {})

    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Executive snapshot")
    st.caption("High-level portfolio health with prioritized next actions.")

    if df_filtered is None or df_filtered.empty:
        st.info("No leads match the current filters. Adjust filters in the sidebar.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

    total = len(df_filtered)
    vip_count = int((df_filtered["Category"] == "VIP Priority").sum())
    hot_count = int((df_filtered["Category"] == "Hot Pipeline").sum())
    nurture_count = int((df_filtered["Category"] == "Nurture List").sum())
    avg_prob = float(df_filtered["Probability"].mean()) * 100.0
    actual_rate = float(df_filtered["Purchase"].mean()) * 100.0 if "Purchase" in df_filtered.columns else np.nan
    overdue_30 = int((df_filtered["Last_Contact_Days"] >= 30).sum()) if "Last_Contact_Days" in df_filtered.columns else 0
    attrition = int((df_filtered["Attrition_Risk"] == 1).sum()) if "Attrition_Risk" in df_filtered.columns else 0
    vip_at_risk = (
        int(((df_filtered["Category"] == "VIP Priority") & (df_filtered["Last_Contact_Days"] >= 14)).sum())
        if "Last_Contact_Days" in df_filtered.columns
        else 0
    )

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
    r1, r2, r3 = st.columns(3, gap="medium")
    with r1:
        kpi_card("Overdue follow-ups", f"{overdue_30:,}", "≥ 30 days since last contact", "risk")
    with r2:
        kpi_card("Attrition risk", f"{attrition:,}", "Flagged leads requiring retention", "risk")
    with r3:
        kpi_card("VIP at risk", f"{vip_at_risk:,}", "VIP with ≥ 14 days no contact", "risk")

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### Board-ready summary")
    st.caption("A concise narrative you can paste into an exec email or slide.")

    # Baseline deltas vs full portfolio (unfiltered)
    if df_scored is not None and not df_scored.empty:
        base_total = len(df_scored)
        base_vip = int((df_scored["Category"] == "VIP Priority").sum()) if "Category" in df_scored.columns else 0
        base_avg = float(df_scored["Probability"].mean()) * 100.0 if "Probability" in df_scored.columns else np.nan
        base_actual = float(df_scored["Purchase"].mean()) * 100.0 if "Purchase" in df_scored.columns else np.nan
    else:
        base_total = 0
        base_vip = 0
        base_avg = np.nan
        base_actual = np.nan

    vip_share = vip_count / max(total, 1) * 100.0
    base_vip_share = base_vip / max(base_total, 1) * 100.0 if base_total else np.nan
    vip_share_delta = vip_share - base_vip_share if np.isfinite(base_vip_share) else np.nan
    avg_delta = avg_prob - base_avg if np.isfinite(base_avg) else np.nan
    actual_delta = actual_rate - base_actual if np.isfinite(base_actual) else np.nan

    bullets = [
        f"Portfolio health is {avg_prob:.1f}% avg predicted probability "
        + (f"({avg_delta:+.1f} pts vs full portfolio)." if np.isfinite(avg_delta) else "."),
        f"VIP share is {vip_share:.1f}% of the filtered book "
        + (f"({vip_share_delta:+.1f} pts vs baseline mix)." if np.isfinite(vip_share_delta) else "."),
        f"Immediate execution focus: {overdue_30:,} overdue follow-ups, {attrition:,} attrition-risk leads, "
        f"and {vip_at_risk:,} VIP accounts at risk due to inactivity.",
    ]

    st.markdown("\n".join([f"- {b}" for b in bullets]))

    snapshot = ExecutiveSnapshot(
        generated_at=now_iso_local(),
        leads_filtered=int(total),
        vip=int(vip_count),
        hot=int(hot_count),
        nurture=int(nurture_count),
        avg_prob_pct=float(avg_prob),
        actual_rate_pct=float(actual_rate) if np.isfinite(actual_rate) else 0.0,
        overdue_30=int(overdue_30),
        attrition_risk=int(attrition),
        vip_at_risk=int(vip_at_risk),
        bullets=bullets,
    )
    pdf_bytes = build_executive_snapshot_pdf(snapshot)
    st.download_button(
        "Download executive snapshot (PDF)",
        data=pdf_bytes,
        file_name="apexmotors_executive_snapshot.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

    st.markdown("<br/>", unsafe_allow_html=True)
    left_col, right_col = st.columns([1.15, 0.85], gap="large")

    with left_col:
        st.markdown("#### Tier distribution")
        fig, ax = plt.subplots(figsize=(10, 5.5))
        sns.countplot(
            data=df_filtered,
            x="Category",
            palette=tier_colors,
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
            palette=tier_colors,
            ax=ax2,
        )
        ax2.set_xlabel("Predicted purchase probability")
        ax2.set_ylabel("Lead count")
        apply_exec_dark_style(ax2)
        sns.despine()
        plt.tight_layout()
        st.pyplot(fig2, use_container_width=True)

    st.markdown("<br/>", unsafe_allow_html=True)
    st.markdown("#### Next actions (operational)")
    a1, a2, a3 = st.columns([1, 1, 1], gap="large")
    with a1:
        st.markdown("**1) Clear overdue outreach backlog**")
        st.write(f"Prioritize {overdue_30:,} leads with ≥30 days since last contact.")
    with a2:
        st.markdown("**2) Retain high-value at-risk leads**")
        if "Attrition_Risk" in df_filtered.columns:
            st.write(f"Launch retention actions for {attrition:,} flagged leads.")
        else:
            st.write("Attrition_Risk not available in this dataset.")
    with a3:
        st.markdown("**3) Close VIP opportunities**")
        top_vip = df_filtered[df_filtered["Category"] == "VIP Priority"].sort_values("Probability", ascending=False).head(5)
        if top_vip.empty:
            st.write("No VIP leads under current filters.")
        else:
            cols = ["Lead_ID", "Probability"]
            if "Last_Contact_Days" in top_vip.columns:
                cols.append("Last_Contact_Days")
            st.dataframe(top_vip[cols], use_container_width=True, hide_index=True)

    st.markdown("</div>", unsafe_allow_html=True)


main()

