# ApexMotors Revenue Intelligence Engine (v3.0) 🏎️  
**Scaling Sales Efficiency through Gradient Boosting & Dimensionality Reduction**  

## Quick start (run the Command Center)

This public repo **does not ship** CRM exports or model binaries. You can still run the app locally in two ways:

1. **Clone and install**

```bash
git clone https://github.com/rikigarcia/ApexMotors_Revenue_Intelligence.git
cd ApexMotors_Revenue_Intelligence
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
```

2. **Choose one path**

- **Instant demo (recommended first run):** run `streamlit run src/app.py`, then turn on **Demo mode (synthetic leads)** on the first screen (or in the sidebar). No `data/` or `models/` files required.
- **Your own data:** add `data/processed/apex_leads_final_v3.csv` (and optionally `models/xgb_champion_v3.joblib` for XGBoost scoring). Or build the processed file from raw input: `python scripts/build_processed_data.py` (see step 3 under Installation).

3. **Launch**

```bash
streamlit run src/app.py
```

## 📌 Project Overview  
The **ApexMotors Revenue Intelligence Engine** is a machine learning solution designed to transform lead management from a reactive "Lead Fatigue" state into a proactive "Strategic Prioritization" model.

- **Business context**: ApexMotors processes **10,000+ leads/month** (operational framing).
- **Project dataset**: the reference design uses a **1,200-lead** sample (binary purchase target; ~17% purchasers). **Sample CSVs are not committed** to this repo; use Demo mode or supply your own files locally.

The system learns a purchase propensity score and maps it into a tiered outreach strategy (VIP / Hot / Nurture / Passive). The champion model improves **F1 from 0.52 → 0.59** over a Logistic Regression baseline (13.3% relative gain).  
## 🚀 Key Features  
* **Predictive Lead Scoring**: Utilizes an optimized **XGBoost** champion model to identify "VIP" and "Hot" leads.  
* **Dimensionality Reduction (Exploratory)**: Uses **PCA** for 2D visualization and signal inspection (explains ~51.64% variance with 2 components in the notebook analysis).  
* **Explainable AI (XAI)**: Integrated **SHAP** analysis to provide transparency into model decision-making.  
* **Ethical AI Audit**: Validated for fairness with a **1.02 Disparate Impact Ratio**, ensuring unbiased lead prioritization.  
* **Automation Matrix**: A 3-tier action framework (VIP, Hot, Nurture) for automated marketing workflows.  
## 🛠️ Tech Stack  
* **Language**: Python 3.9+  
* **Libraries**: Scikit-Learn, XGBoost, SHAP, Pandas, NumPy, Matplotlib, Seaborn  
* **Deployment**: Streamlit (Dashboard), Joblib (Serialization), Cloudflare (Tunneling)  
* **Environment**: Google Colab / Local Python environment  
## 📁 Directory Structure (Step 7 Portability)  
Following open-source standards, this project uses a root-relative hierarchy:  

```
├── data/
│   ├── raw/            # Original CRM dataset (local only; not committed)
│   └── processed/      # Cleaned and engineered features (local only; not committed)
├── models/
│   └── xgb_champion_v3.joblib  # Serialized model (local only; not committed)
├── notebooks/
│   ├── 01_Framing.ipynb
│   ├── 02_EDA_PCA.ipynb
│   ├── 03_Feature_Engineering.ipynb
│   ├── 04_Modeling_Tuning.ipynb
│   └── 05_Bias_Ethics_SHAP.ipynb
├── scripts/
│   └── build_processed_data.py  # Rebuilds data/processed artifact from raw CSV
├── src/
│   ├── app.py          # Streamlit multi-page production app (entrypoint)
│   ├── core.py         # Data/model loading + scoring + filtering
│   ├── styles.py       # Global “CEO-grade” theme
│   ├── ui_components.py# Reusable UI components (topbar, KPI cards)
│   ├── dashboard.py    # Legacy redirect to the new app entrypoint
│   └── pages/          # Streamlit pages (Overview, Segments, Explorer, Strategy)
├── requirements.txt    # Reproducible environment configuration
└── README.md           # Project documentation
```

## 🔒 Security & data hygiene (public repo)
- **Do not commit real CRM exports** (raw or processed). Keep `data/` and `models/` local.
- Use **Demo mode (synthetic leads)** in the app when the dataset is not present.
- Never commit secrets (API keys/tokens). Streamlit secrets belong in `.streamlit/secrets.toml` (ignored).
- See `SECURITY.md` for reporting and data-handling policy.
## ⚙️ Installation & Usage  

For the fastest first run (no data files), use **Quick start** above and enable **Demo mode** in the app.

1. **Clone the repository**

```bash
git clone https://github.com/rikigarcia/ApexMotors_Revenue_Intelligence.git
cd ApexMotors_Revenue_Intelligence
```

2. **Create a virtual environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

3. **Build (or rebuild) the processed dataset artifact**

```bash
python scripts/build_processed_data.py
```

This writes:
- `data/processed/apex_leads_final_v3.csv`
- `data/processed/apex_leads_final_v3.schema.json` (row count, null counts, dtypes)

4. **Run the production app**

```bash
streamlit run src/app.py
```

### macOS note (XGBoost model loading)
If the dashboard warns that the model could not be loaded (rules-based fallback), install the OpenMP runtime:

```bash
brew install libomp
```

## 📊 Business Impact (ROI)  
* **Efficiency Gain**: Predicted **15-20% increase** in sales team productivity by reducing manual lead sorting.  
* **Revenue Growth**: Strategic focus on leads with >85% purchase probability to maximize conversion rates.  
## ⚖️ Ethical Certification  
This model has been audited across sensitive lead sources and satisfies the **"Four-Fifths Rule"** for algorithmic fairness, maintaining a Disparate Impact Ratio of **1.02**.  
