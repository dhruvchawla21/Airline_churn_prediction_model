# Airline Loyalty Churn Prediction & Retention Dashboard

A machine learning pipeline that predicts customer churn risk in an airline loyalty program, segments customers into actionable groups, and surfaces insights through an interactive retention dashboard for marketing teams.

---

## Overview

This project addresses a core airline retention problem: identifying which loyalty members are likely to disengage before they actually leave. It combines behavioral feature engineering, gradient boosting, and a non-technical dashboard so marketing managers can prioritize outreach without touching any code.

**Live dashboard:** [airlinechurnpredictionmodel-21.streamlit.app](https://airlinechurnpredictionmodel-21.streamlit.app)

**Key results:**
- ROC AUC of **0.752** on held-out test data
- Top 10% riskiest customers capture **50% of all churners** (5× lift over random)
- 13,191 customers scored, segmented, and ready for campaign targeting

---

## Project Structure

```
CNA_summer_project/
├── Final_pipeline.ipynb              # End-to-end ML pipeline
├── retention_app.py                  # Streamlit retention dashboard
├── final_customer_results.csv        # Scored + segmented customer output
├── Customer_Flight_Activity.csv      # Raw monthly flight transaction data
├── Customer_Loyalty_History.csv      # Raw customer master / demographics
├── Calendar.csv                      # Reference calendar for temporal joins
└── Airline_Loyalty_Data_Dictionary.csv  # Data dictionary for all fields
```

---

## Pipeline (`Final_pipeline.ipynb`)

The notebook runs end-to-end in 8 phases:

| Phase | Description |
|-------|-------------|
| 1–2 | **Data cleaning** — deduplication (3,871 duplicates removed), negative salary fix, constant column removal |
| 3 | **Cohort definition** — customers with ≥1 flight in Jul 2017–Jun 2018 and not cancelled by June 2018 (13,191 members) |
| 4 | **Churn label** — churn = no flights in H2 2018 OR cancelled in H2 2018 (422 churners, 3.2% base rate) |
| 5 | **Feature engineering** — 41 features across recency, frequency, momentum, decay, distance, points engagement, regularity, seasonal activity, and demographics |
| 6 | **Modeling** — XGBoost with class-weight balancing; 5-fold stratified CV; F1/F2-optimized thresholds |
| 7 | **Scoring** — 5-seed ensemble refit on full labeled data; all customers scored |
| 8 | **Segmentation** — 6 risk-value segments with a defined retention action playbook per segment |

### Feature Groups

- **Recency:** Months since last flight, current inactive streak
- **Frequency:** Flights at 3m / 6m / 12m windows
- **Momentum:** 6-month trend, recency-to-history ratio, share of recent activity
- **Decay:** Recency-weighted activity (recent flights weighted more)
- **Engagement:** Points accumulation, redemption, redemption ratio, ever-redeemed flag
- **Regularity:** Longest zero-run, volatility (std, CV, concentration index)
- **Seasonal:** Peak-season flight share (Jun–Aug, Dec), quarter concentration (from Calendar.csv)
- **Demographics:** Card tier, education, marital status, gender, enrollment type (all one-hot encoded)

> CLV and salary are excluded from model features to avoid leakage; CLV is used only for downstream value segmentation.

### Model Performance

| Metric | Value |
|--------|-------|
| ROC AUC | 0.752 |
| PR AUC | 0.167 |
| Churners in top 10% risk | ~50% |
| Churners in top 20% risk | ~61% |

**Top predictive features:** longest inactive streak (13%), enrollment type (6%), recent points ratio (3.6%), ever redeemed (3.2%), tenure (3.1%)

### Customer Segments

| Segment | Count | Description |
|---------|-------|-------------|
| VIP at risk | 346 | High-value, high churn probability |
| At risk | 873 | Lower-value, high churn probability |
| High-value cooling | 902 | High-value, medium churn probability |
| Cooling | 2,198 | Lower-value, medium churn probability |
| High-value healthy | 2,711 | High-value, low churn probability |
| Healthy | 6,161 | Lower-value, low churn probability |

---

## Dashboard (`retention_app.py`)

A Streamlit app designed for non-technical marketing and retention managers.

**To run:**
```bash
streamlit run retention_app.py
```

### Tabs

1. **Header KPIs** — Total active members, high-risk count, VIPs at risk, total CLV exposed
2. **Action List** — Filterable table by segment and card tier; adjustable contact capacity slider (50–3,000); CSV export for campaign teams
3. **Segment Playbook** — Per-segment member count, disengagement rate, average CLV, and standing retention instruction
4. **Member Lookup** — Search by loyalty number; shows risk score, segment, CLV, flight stats, tenure, and recommended next action

---

## Setup

### Requirements

```bash
pip install -r requirements.txt
```

### Run the pipeline

Open `Final_pipeline.ipynb` in Jupyter and run all cells. This regenerates `final_customer_results.csv`.

```bash
jupyter notebook Final_pipeline.ipynb
```

### Run the dashboard

```bash
streamlit run retention_app.py
```

> The dashboard reads `final_customer_results.csv` — run the pipeline first if this file is absent or outdated.

---

## Data

| File | Rows | Description |
|------|------|-------------|
| `Customer_Flight_Activity.csv` | 392,937 | Monthly flight transactions (Jul 2016–Dec 2018): flights, distance, points earned/redeemed |
| `Customer_Loyalty_History.csv` | 16,738 | Customer master: demographics, card tier, CLV, enrollment/cancellation dates |
| `Calendar.csv` | — | Date dimension table used to derive quarter and seasonal features |
| `Airline_Loyalty_Data_Dictionary.csv` | — | Field definitions for all input tables |

All data files are included in this repository. Place them in the project root alongside the notebook.

---

## Tech Stack

- **Python 3.x**
- **pandas / numpy** — Data wrangling and feature engineering
- **scikit-learn** — Cross-validation, metrics, train-test split
- **XGBoost** — Gradient boosted classifier
- **Streamlit** — Interactive retention dashboard
- **Jupyter** — Pipeline development environment

---
