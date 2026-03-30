# ApexMotors Revenue Intelligence Engine (v3.0) 🏎️  
**Scaling Sales Efficiency through Gradient Boosting & Dimensionality Reduction**  
## 📌 Project Overview  
The **ApexMotors Revenue Intelligence Engine** is a machine learning solution designed to transform lead management from a reactive "Lead Fatigue" state into a proactive "Strategic Prioritization" model. By analyzing over 10,000 lead records, this system identifies high-intent purchasers with a **13.3% performance gain** over baseline methods, allowing sales teams to focus on leads with the highest conversion probability.  
## 🚀 Key Features  
* **Predictive Lead Scoring**: Utilizes an optimized **XGBoost** champion model to identify "VIP" and "Hot" leads.  
* **Dimensionality Reduction**: Employs **Principal Component Analysis (PCA)** to reduce feature noise while capturing 90% of data variance.  
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
│   ├── raw/            # Original CRM dataset
│   └── processed/      # Cleaned and engineered features
├── models/
│   └── xgb_champion_v3.joblib  # Serialized production model
├── notebooks/
│   ├── 01_Framing.ipynb
│   ├── 02_EDA_PCA.ipynb
│   ├── 03_Feature_Engineering.ipynb
│   ├── 04_Modeling_Tuning.ipynb
│   └── 05_Bias_Ethics_SHAP.ipynb
├── src/
│   └── dashboard.py    # Streamlit Command Center code
├── requirements.txt    # Reproducible environment configuration
└── README.md           # Project documentation

```
## ⚙️ Installation & Usage  
1. **Clone the Repository**: git clone [https://github.com/your-username/ApexMotors-Revenue-Intelligence.git](https://github.com/your-username/ApexMotors-Revenue-Intelligence.git)  
2.   
3. **Install Dependencies**: pip install -r requirements.txt  
4.   
5. **Run the Dashboard**: streamlit run src/dashboard.py  
6.   
## 📊 Business Impact (ROI)  
* **Efficiency Gain**: Predicted **15-20% increase** in sales team productivity by reducing manual lead sorting.  
* **Revenue Growth**: Strategic focus on leads with >85% purchase probability to maximize conversion rates.  
## ⚖️ Ethical Certification  
This model has been audited across sensitive lead sources and satisfies the **"Four-Fifths Rule"** for algorithmic fairness, maintaining a Disparate Impact Ratio of **1.02**.  
