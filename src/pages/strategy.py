from __future__ import annotations

import streamlit as st


def main() -> None:
    st.markdown("<div class='apex-card'>", unsafe_allow_html=True)
    st.markdown("### Automation matrix & strategic logic")

    vip = float(st.session_state.get("vip_th", 0.85))
    hot = float(st.session_state.get("hot_th", 0.60))
    nurture = float(st.session_state.get("nurture_th", 0.40))

    st.markdown(
        f"""
The **Apex Automation Matrix** assigns each lead to an automated workflow based on the predicted probability:

- **VIP Priority (≥ {vip:.0%})**: immediate alert to sales manager; concierge outreach; premium preview invite.
- **Hot Pipeline (≥ {hot:.0%})**: 24-hour callback SLA; retargeting based on configuration signals.
- **Nurture List (≥ {nurture:.0%})**: multi-touch education drip; progressive profiling.
- **Passive (< {nurture:.0%})**: brand-only cadence to minimize operational cost.
        """
    )

    with st.expander("Model/runtime notes"):
        st.write(
            "- If the XGBoost artifact can’t load, scoring falls back to a rules-based method for transparency.\n"
            "- On macOS, install `libomp` if you want to load the saved model artifact."
        )

    st.markdown("</div>", unsafe_allow_html=True)


main()

