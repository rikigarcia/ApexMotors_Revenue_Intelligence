from __future__ import annotations

import streamlit as st


def inject_global_css() -> None:
    st.markdown(
        """
<style>
:root {
  --apex-bg: #0b1220;
  --apex-surface: #0f172a;
  --apex-card: rgba(255, 255, 255, 0.06);
  --apex-card-2: rgba(255, 255, 255, 0.08);
  --apex-border: rgba(226, 232, 240, 0.14);
  --apex-text: #e5e7eb;
  --apex-muted: rgba(226, 232, 240, 0.72);
  --apex-shadow: 0 14px 28px rgba(0,0,0,0.45);
  --apex-radius: 16px;
  --apex-brand: #111827;
  --apex-gold: #d6b36a;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

.main { background: radial-gradient(1000px 700px at 12% 6%, rgba(214,179,106,0.10) 0%, rgba(11,18,32,0.0) 60%),
                 radial-gradient(1100px 800px at 90% 20%, rgba(91,192,222,0.08) 0%, rgba(11,18,32,0.0) 55%),
                 var(--apex-bg); }

/* Layout */
.block-container {
  padding-top: 1.25rem;
  padding-bottom: 1.25rem;
  padding-left: 3.2rem;
  padding-right: 3.2rem;
}

/* Typography */
html, body, [class*="css"]  { color: var(--apex-text); }
h1, h2, h3 { letter-spacing: -0.02em; }

/* Sidebar */
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(15,23,42,0.98) 0%, rgba(11,18,32,0.98) 100%);
  border-right: 1px solid var(--apex-border);
}
section[data-testid="stSidebar"] .block-container {
  padding-top: 1.25rem;
  padding-left: 1.15rem;
  padding-right: 1.15rem;
}

/* Topbar */
.apex-topbar {
  background: linear-gradient(135deg, rgba(17,24,39,0.85) 0%, rgba(15,23,42,0.75) 100%);
  border: 1px solid var(--apex-border);
  border-radius: var(--apex-radius);
  padding: 18px 18px;
  box-shadow: var(--apex-shadow);
  margin-bottom: 14px;
}
.apex-topbar-title { font-size: 1.22rem; font-weight: 900; color: #ffffff; margin: 0; line-height: 1.2; }
.apex-topbar-subtitle { font-size: 0.96rem; color: var(--apex-muted); margin: 8px 0 0 0; }
.apex-badges { margin-top: 12px; display: flex; gap: 8px; flex-wrap: wrap; }
.apex-badge {
  display: inline-flex; align-items: center; gap: 8px;
  padding: 6px 10px; font-size: 0.82rem; border-radius: 999px;
  border: 1px solid var(--apex-border);
  color: rgba(255,255,255,0.88);
  background: rgba(255,255,255,0.06);
}
.apex-badge.gold { border-color: rgba(214,179,106,0.55); color: rgba(214,179,106,0.95); }

/* Cards */
.apex-card {
  background: linear-gradient(180deg, var(--apex-card-2) 0%, var(--apex-card) 100%);
  border: 1px solid var(--apex-border);
  border-radius: var(--apex-radius);
  padding: 18px 18px;
  box-shadow: 0 14px 24px rgba(0,0,0,0.35);
}

/* KPI cards */
.apex-kpi {
  background: linear-gradient(180deg, rgba(255,255,255,0.09) 0%, rgba(255,255,255,0.06) 100%);
  border: 1px solid var(--apex-border);
  border-radius: 18px;
  padding: 14px 14px;
  box-shadow: 0 10px 16px rgba(0,0,0,0.28);
}
.apex-kpi .label { color: var(--apex-muted); font-size: 0.78rem; font-weight: 800; text-transform: uppercase; letter-spacing: 0.08em; }
.apex-kpi .value { font-size: 1.65rem; font-weight: 950; color: #ffffff; margin-top: 8px; line-height: 1.1; }
.apex-kpi .sub { color: var(--apex-muted); font-size: 0.88rem; margin-top: 7px; }
.apex-kpi.vip { border-top: 3px solid #ef4444; }
.apex-kpi.hot { border-top: 3px solid #f59e0b; }
.apex-kpi.nurture { border-top: 3px solid #38bdf8; }
.apex-kpi.health { border-top: 3px solid var(--apex-gold); }
.apex-kpi.total { border-top: 3px solid rgba(226,232,240,0.6); }
.apex-kpi.risk { border-top: 3px solid #fb7185; }

/* Dataframe polish */
div[data-testid="stDataFrame"] { border: 1px solid var(--apex-border); border-radius: 14px; overflow: hidden; }

</style>
        """.strip(),
        unsafe_allow_html=True,
    )

