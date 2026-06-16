# 📉 Customer Churn Analysis & Revenue Impact Dashboard
 
> **An end-to-end data analytics project** — from raw customer data to a business-ready dashboard and ROI analysis — built using Python, SQL, and Power BI.
 
---
 
## 🔍 Project Overview
 
A telecom company is losing customers every month. This project analyses **7,032 customer records** to identify *who* is likely to churn, *why* they leave, and *how much revenue* is at risk — then delivers actionable recommendations with a calculated ROI.
 
This is not just an EDA exercise. Every finding is tied to a **business outcome and a dollar figure**.
 
---
 
## 📊 Dashboard Preview
 
<img width="1162" height="653" alt="image" src="https://github.com/user-attachments/assets/35d5e12e-f51c-4a35-93cb-a3bfad485ebe" />

 
**Live filters:** Use the Contract Type slicer to dynamically explore churn patterns across customer segments.
 
---
 
## 💡 Key Findings
 
| Metric | Value |
|---|---|
| Overall Churn Rate | **26.5%** — 1 in 4 customers is leaving |
| Annual Revenue Lost | **$1.7M+** from already-churned customers |
| High Risk Active Customers | **~1,300** customers at imminent risk |
| Monthly Revenue at Risk | **$23,390+** in recoverable monthly revenue |
| ROI of Retention Intervention | **300%+** at a $10/customer intervention cost |
 
> 💬 *Assuming a 30% retention rate on High Risk customers with a $10/customer outreach cost.*
 
---
 
## 🛠️ Tools & Technologies
 
| Tool | Purpose |
|---|---|
| **Python (pandas)** | Data cleaning, EDA, feature engineering |
| **Matplotlib & Seaborn** | Exploratory visualisations (5 charts) |
| **SQLite + SQL** | Risk scoring model, business queries |
| **Power BI Desktop** | Interactive dashboard with slicers |
| **Jupyter Notebook** | End-to-end analysis environment |
 
---
 

## 🔬 Methodology
 
### Step 1 — Business Framing
Defined the problem statement, KPIs, and key questions before touching any data.
 
### Step 2 — Exploratory Data Analysis
Cleaned 7,043 records (removed 11 with missing billing data). Built 5 visualisations covering churn distribution, contract type, tenure, monthly charges, and correlations.
 
### Step 3 — SQL Risk Scoring Model
Loaded cleaned data into SQLite. Wrote 4 business SQL queries. Built a rule-based churn risk model classifying every customer as **High / Medium / Low Risk** using contract type, tenure, and monthly charges.
 
**Risk tier validation:**
 
| Risk Tier | Customers | Actual Churn Rate |
|---|---|---|
| 🔴 High Risk | ~1,300 | ~55–65% |
| 🟡 Medium Risk | ~2,800 | ~25–35% |
| 🟢 Low Risk | ~2,900 | ~5–8% |
 
### Step 4 — Revenue Impact Calculator
Quantified the business cost of churn and the ROI of acting on the model's findings.
 
```
Revenue Already Lost (Annual)  = Churned customers × Avg monthly charge × 12
Revenue at Risk (Monthly)      = High Risk active customers × Avg monthly charge
Net Recoverable Revenue        = Revenue at Risk × 30% retention − $10 × customers
```
 
### Step 5 — Power BI Dashboard
Built an interactive 4-visual dashboard with 3 KPI cards and a contract type slicer.
---
## 📡 Customer Churn Intelligence Dashboard

An interactive Streamlit web app built on the IBM Telco Customer Churn dataset (7,032 customers).
Two pages — a **Risk Dashboard** and a **Revenue Simulator** — that turn churn data into business decisions.

**Live Demo:** https://customer-churn-analysis-929.streamlit.app/

---
 
## What's Inside
 
### Page 1 — Risk Dashboard
- KPIs: Churn rate, annual revenue lost, high-risk count, recoverable revenue/month
- Risk tier distribution (donut chart)
- Churn rate by contract type (bar chart)
- Churn rate by tenure band (line chart)
- Monthly charges: churned vs retained (box plot)
- Top 50 high-risk active customers by revenue at stake (filterable table)
- Churn driver heatmap across 9 service features
### Page 2 — Revenue Simulator
- Current state snapshot (annual revenue lost, avg lost LTV, high-risk pool)
- Intervention parameter controls (target segment, retention %, cost/customer, LTV horizon)
- Live ROI calculation with net benefit
- ROI vs retention rate sensitivity chart
- Revenue saved by LTV horizon (bar + cost line)
- Cost sensitivity table (ROI matrix across cost × retention rate)
- Automated business recommendation (Strong Buy / Recommended / Marginal / Not Viable)

---
 
## 📌 Business Recommendations
 
1. **Prioritise month-to-month customers** — 42.7% churn rate vs 2.8% for two-year contracts. Offer incentives to upgrade contract length.
2. **Focus retention on the first 12 months** — the majority of churn happens within the first year. A structured onboarding programme would reduce early churn significantly.
3. **Target high-charge customers immediately** — churned customers pay ~$18/month more than retained ones. High-value customers are leaving at a disproportionate rate. Personalised outreach for customers paying >$65/month with month-to-month contracts should be the first intervention.
4. **Implement the risk scoring model in production** — the SQL rule-based model requires no ML infrastructure and can run on existing databases. A monthly batch job would keep the High Risk list current.
---
 
## 📂 Dataset
 
**IBM Telco Customer Churn Dataset**
- Source: [Kaggle — blastchar/telco-customer-churn](https://www.kaggle.com/datasets/blastchar/telco-customer-churn)
- Rows: 7,043 customers
- Columns: 21 features (demographics, services, billing, churn label)
- Licence: Open / Public use
---
 
## 👤 About
 
Built by **[AVALA NAGA VENKATA SASI KUMAR]** as part of a self-directed data analytics project.
 
- 📧 Email: [anvsasikumar19@gmail.com]
---
 
 
