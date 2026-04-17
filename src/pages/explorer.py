from __future__ import annotations

import streamlit as st


def main() -> None:
    df_filtered = st.session_state.get("df_filtered")

    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Lead explorer + CRM export")

    if df_filtered is None or df_filtered.empty:
        st.info("No leads match the current filters.")
        st.markdown("</div>", unsafe_allow_html=True)
        return

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
    for extra in ["Lead_Source", "Lead_Temperature", "Last_Contact_Days", "Attrition_Risk"]:
        if extra in export_df.columns:
            export_payload_cols.append(extra)

    csv_bytes = export_df[export_payload_cols].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="Download filtered CSV",
        data=csv_bytes,
        file_name="apexmotors_filtered_leads.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("</div>", unsafe_allow_html=True)


main()

