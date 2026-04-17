# FINAL NARRATIVE REPORT: ApexMotors Revenue Intelligence (v3.0)

**Author:** Enrique Garcia
**Date:** March 2026
**Subject:** Capstone Project Executive Summary & Ethical Audit

---

## 1. Problem Statement & Framing
ApexMotors faced a significant operational bottleneck: "Lead Fatigue." With over 10,000 monthly leads, the sales team struggled to identify high-intent buyers, leading to revenue leakage and wasted human resources. This project frames the challenge as a **Binary Classification** task, aiming to predict purchase probability and automate lead prioritization.

## 2. Methodology & Technical Rigor
The project followed a rigorous machine learning lifecycle:
* **EDA & Preprocessing:** Identified key drivers such as `Test_Drive_Completed` and `Web_Configurator_Status`. Addressed class imbalance using **SMOTE**.
* **Dimensionality Reduction (Exploratory):** Utilized **PCA** for visualization and signal inspection (the deployed model is trained on the engineered feature set rather than PCA components).
* **Modeling:** Compared a Logistic Regression baseline (F1: 0.52) against an optimized **XGBoost** champion model.
* **Optimization:** Selected and justified champion hyperparameters and evaluated the model with standard classification reporting, achieving a **Champion F1-Score of 0.59** (a 13.3% improvement over baseline).

## 3. Explainability & Ethical Audit (Step 5)
To ensure transparency, **SHAP (Shapley Additive Explanations)** was used to visualize feature importance, confirming that purchase predictions are driven by behavioral intent signals. 
A formal **Bias Audit** was conducted across sensitive lead sources. The model achieved a **Disparate Impact Ratio (DIR) of 1.02**, satisfying the "Four-Fifths Rule" and ensuring equitable treatment of all prospects regardless of their origin.

## 4. Business Impact & ROI
The "Apex Automation Matrix" categorizes leads into three strategic tiers:
* **VIP Priority (>85%):** Immediate Sales Manager alerts.
* **Hot Leads (60-84%):** Targeted retargeting and 24-hour callbacks.
* **Nurture (40-59%):** Automated email education drips.

**Conclusion:** The system provides a predicted **15-20% gain in sales efficiency**, allowing the human sales force to focus exclusively on high-probability revenue opportunities.

## 5. Deployment & Technical Stack
The system is production-ready and fully reproducible.
* **Framework:** Python, Scikit-Learn, XGBoost, SHAP.
* **Interface:** Streamlit **multi-page Executive Command Center** designed for CEO-level portfolio oversight and export-ready operational workflows (filters, segment performance, lead explorer, and strategy tiering).
* **Environment:** Managed via `requirements.txt` for portability across local and cloud environments.

### Executive-grade UX (v3.0 Command Center)
The deployed interface is structured as a production-style app:
* **Overview:** executive snapshot, portfolio health distribution, and next actions (overdue contacts, attrition risk, top VIP leads).
* **Segments:** actual purchase-rate vs predicted probability by tier, plus lead-source mix.
* **Lead Explorer:** search, export-ready filtered tables, and CRM-friendly CSV downloads.
* **Strategy:** configurable tier thresholds aligned to the Apex Automation Matrix.

## 6. Generative AI Utilization (Step 9)
In accordance with the project requirements, Generative AI was utilized to:
* **Documentation:** Drafting the professional README.md and folder hierarchy.
* **Communication:** Synthesizing technical metrics into executive-facing ROI visuals and strategy summaries.
* **Explainability:** Assisting in the interpretation of fairness metrics and SHAP summary plots.
All machine learning logic, model training, and performance validation were executed and verified by the author.