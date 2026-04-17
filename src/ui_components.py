from __future__ import annotations

import streamlit as st


def kpi_card(label: str, value: str, sub: str, tone: str) -> None:
    st.markdown(
        f"""
<div class="apex-kpi {tone}">
  <div class="label">{label}</div>
  <div class="value">{value}</div>
  <div class="sub">{sub}</div>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )


def topbar() -> None:
    st.markdown(
        """
<div class="apex-topbar">
  <p class="apex-topbar-title">ApexMotors • Revenue Intelligence Command Center</p>
  <p class="apex-topbar-subtitle">Portfolio health, segmentation, and export-ready lead operations</p>
  <div class="apex-badges">
    <span class="apex-badge gold">v3.0</span>
    <span class="apex-badge">Executive view</span>
    <span class="apex-badge">Export-ready</span>
  </div>
</div>
        """.strip(),
        unsafe_allow_html=True,
    )

