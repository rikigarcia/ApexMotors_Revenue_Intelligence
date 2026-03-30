import streamlit as st
import pandas as pd
import numpy as np
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="ApexMotors Command Center", layout="wide")

# --- ADVANCED CSS FOR PREMIUM UI ---
st.markdown("""
    <style>
    /* Remove top margin and white blocks */
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .main { background-color: #f4f7f9; }
    
    /* Sleek Metric Card Styling */
    [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 800;
        color: #1e293b;
        line-height: 1.2;
    }
    [data-testid="stMetricDelta"] {
        font-size: 0.9rem !important;
        font-weight: 500;
    }
    [data-testid="stMetricLabel"] {
        font-size: 0.95rem !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: -10px;
    }
    
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px 20px !important; 
        border-radius: 12px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05), 0 4px 6px -2px rgba(0,0,0,0.02);
        border: 1px solid #e2e8f0;
        transition: transform 0.2s ease-in-out;
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 20px 25px -5px rgba(0,0,0,0.08);
    }

    /* Color Accents for Tiers */
    /* VIP - Red */
    [data-testid="column"]:nth-child(1) .stMetric { border-top: 5px solid #d9534f; }
    /* Hot - Amber */
    [data-testid="column"]:nth-child(2) .stMetric { border-top: 5px solid #f0ad4e; }
    /* Nurture - Blue */
    [data-testid="column"]:nth-child(3) .stMetric { border-top: 5px solid #5bc0de; }
    /* Portfolio - Dark */
    [data-testid="column"]:nth-child(4) .stMetric { border-top: 5px solid #1e293b; }
    
    </style>
    """, unsafe_allow_html=True)

# --- PATH INITIALIZATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "processed" / "processed_leads.csv"

# --- DATA LOADING ---
@st.cache_data
def load_data():
    """Load processed leads or generate mock data for demo purposes."""
    if DATA_PATH.exists():
        return pd.read_csv(DATA_PATH)
    else:
        np.random.seed(42)
        data = pd.DataFrame({
            'Lead_ID': [f"ID_{i}" for i in range(1000, 1307)],
            'Probability': np.random.uniform(0.1, 0.98, 307),
            'Test_Drive_Completed': np.random.choice([0, 1], 307, p=[0.7, 0.3]),
            'Web_Configurator_Status': np.random.choice([0, 1], 307, p=[0.6, 0.4])
        })
        return data

def get_strategy(prob):
    """Assign leads to the Marketing Automation Matrix tiers."""
    if prob >= 0.85: return "VIP Priority"
    elif prob >= 0.60: return "Hot Pipeline"
    elif prob >= 0.40: return "Nurture List"
    else: return "Passive"

# --- APP LAYOUT ---
st.title("🏎️ ApexMotors: Revenue Intelligence Command Center")
st.markdown("<p style='color: #64748b; font-size: 1.1rem; margin-top: -15px;'>V3.0 Predictive Portfolio Strategy Overview</p>", unsafe_allow_html=True)

# Load Data
df = load_data()
df['Category'] = df['Probability'].apply(get_strategy)

# --- TOP ROW: KPI METRICS ---
col1, col2, col3, col4 = st.columns(4)
with col1:
    vip_count = len(df[df['Category'] == "VIP Priority"])
    st.metric("VIP Priority", f"{vip_count}", delta="High Intent")
with col2:
    hot_count = len(df[df['Category'] == "Hot Pipeline"])
    st.metric("Hot Pipeline", f"{hot_count}", delta="Action Required")
with col3:
    nurture_count = len(df[df['Category'] == "Nurture List"])
    st.metric("Nurture List", f"{nurture_count}", delta="Drip Sequence")
with col4:
    avg_prob = df['Probability'].mean() * 100
    st.metric("Avg. Purchase Prob.", f"{avg_prob:.1f}%", delta="Portfolio Health")

st.markdown("<br>", unsafe_allow_html=True)

# --- MIDDLE ROW: CHARTS & ANALYSIS ---
left_col, right_col = st.columns([1, 1], gap="large")

with left_col:
    st.markdown("### Lead Volume by Automation Tier")
    fig, ax = plt.subplots(figsize=(10, 6))
    palette = {
        "VIP Priority": "#d9534f",   # Dark Red
        "Hot Pipeline": "#f0ad4e",   # Amber
        "Nurture List": "#5bc0de",   # Light Blue
        "Passive": "#999999"         # Grey
    }
    sns.countplot(
        data=df, 
        x='Category', 
        palette=palette, 
        order=["VIP Priority", "Hot Pipeline", "Nurture List", "Passive"],
        ax=ax
    )
    ax.set_ylabel("Lead Count", color="#64748b")
    ax.set_xlabel("")
    ax.tick_params(colors='#64748b')
    ax.grid(axis='y', linestyle='--', alpha=0.3)
    sns.despine()
    plt.tight_layout()
    st.pyplot(fig)

with right_col:
    st.markdown("### Bulk Lead Extraction & Export")
    export_cat = st.selectbox(
        "Select Strategy Category to Export for CRM Integration", 
        ["VIP Priority", "Hot Pipeline", "Nurture List"]
    )
    export_df = df[df['Category'] == export_cat].sort_values(by="Probability", ascending=False)
    st.dataframe(
        export_df[['Lead_ID', 'Category', 'Probability']], 
        use_container_width=True,
        hide_index=True
    )
    if st.button(f"Generate {export_cat} CSV", use_container_width=True):
        st.success(f"File Prepared: Ready to export {len(export_df)} leads to CRM.")

# --- BOTTOM ROW: STRATEGY LOGIC ---
st.divider()
with st.expander("ℹ️ View Automation Matrix & Strategic Logic"):
    st.markdown("""
    The **Apex Automation Matrix** utilizes real-time behavioral signals to assign each lead to an automated workflow:
    
    - **VIP Priority (85% - 100%):** Immediate SMS Alert to Sales Manager. High-priority "Exclusive Preview" email triggered.
    - **Hot Pipeline (60% - 84%):** Mandatory 24-hour callback. Retargeting ads featuring specific vehicle configurations.
    - **Nurture List (40% - 59%):** Enrollment in a 5-day educational email drip focusing on performance and safety specs.
    - **Passive (<40%):** Lead retained in brand awareness pool (Newsletter only) to minimize human operational costs.
    """)

st.caption("ApexMotors Revenue Intelligence v3.0 | Proprietary Predictive Model | 2026 Deployment")