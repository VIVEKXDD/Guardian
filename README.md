# Guardian - AI Risk Manager

**Guardian** is a two-stage AI risk engine designed to reduce merchant losses from returns and RTO (return-to-origin) fraud/abuse in Indian e-commerce.

## Problem Statement

Returns and RTOs represent a significant cost center in Indian e-commerce. 
- Fashion/footwear return rates run roughly 25–40%, particularly elevated during festive sales.
- COD (cash-on-delivery) RTO rates run roughly 20–40% depending on category and pincode.
Existing tooling is largely reactive (e.g., video proof for disputes). Guardian provides a **proactive** layer that scores return risk before an order ships, allowing merchants to take preventative measures without unnecessarily blocking honest customers.

## Architecture Summary

Guardian consists of two stages to balance latency, cost, and reasoning capability:
1. **Stage 1 (Pre-shipment Risk Scorer):** A highly optimized LightGBM model that evaluates an order at placement (using customer history, product details, and geographic RTO rates) to output a raw probability score. If the score is below the operational threshold, it is instantly Auto-Approved.
2. **Stage 2 (LLM Deep Triage):** If the order exceeds the risk threshold, it is routed to an OpenAI-powered reasoning agent. The LLM evaluates the customer's historical patterns and nuances (like sample sizes and payment methods) to output a final decision (`ALLOW` / `VERIFY_MANUALLY` / `RESTRICT_COD`) and a detailed reasoning log.

<p align="center">
  <img src="docs/architecture_diagram.png" alt="Guardian Architecture Diagram" width="500" />
</p>

*For detailed architectural design choices and latency trade-offs, see [ARCHITECTURE.md](docs/ARCHITECTURE.md).*

## Repository Structure

```text
Guardian/
├── data/                      # Synthetic data, feature matrices & train/val/test splits
│   ├── baseline_preds.csv     # Random & baseline benchmark predictions
│   ├── features.csv           # Full engineered feature dataset
│   ├── synthetic_orders.csv   # Raw probabilistic e-commerce orders
│   ├── train.csv              # Isolated training set
│   ├── val.csv                # Isolated validation set (for threshold tuning)
│   └── test.csv               # Frozen holdout test set (unseen evaluation)
├── docs/                      # Technical specifications, diagrams & decision logs
│   ├── plots/                 # EDA distribution & risk correlation charts
│   ├── ARCHITECTURE.md        # Pipeline design, latency analysis & stage separation
│   ├── DATA_NOTES.md          # Synthetic data generation calibration methodology
│   ├── DECISIONS.md           # Architecture Decision Records (ADR log)
│   ├── ISSUES.md              # Post-mortems, bug catches & failure recoveries
│   ├── VIDEO_SCRIPT.md        # 5-minute rubric-aligned video demonstration script
│   ├── stage2_results.md      # Ground truth vs Stage 2 LLM audit logs
│   ├── metrics.txt            # Frozen model benchmark outputs
│   └── architecture_diagram.png # High-resolution architecture visual
├── models/                    # Serialized machine learning artifacts
│   ├── optimal_threshold.txt  # Tuned operational capacity threshold (0.5120)
│   └── stage1_lgbm.txt        # Trained LightGBM Booster model
├── notebooks/                 # Exploratory data analysis & statistical sweeps
│   ├── bootstrap_ci.py        # 1,000-resample bootstrap confidence intervals
│   ├── check_interactions.py  # Feature cross-product & interaction validation
│   ├── eda.py                 # Pincode tier & category risk distribution analysis
│   └── eval_sweep.py          # Operational threshold sweep experiments
├── src/                       # Core production modules
│   ├── api.py                 # FastAPI REST microservice (/score_order)
│   ├── dashboard.py           # Streamlit operational triage UI (with video presets)
│   ├── data_generation.py     # Probabilistic e-commerce transaction generator
│   ├── demo.py                # End-to-end command-line simulation pipeline
│   ├── evaluate.py            # Leakage-free model evaluation runner
│   ├── features.py            # Domain-specific feature engineering transformers
│   ├── split.py               # Leakage-free train/val/test partitioning
│   ├── stage2_llm.py          # Calibrated OpenAI triage reasoning agent
│   ├── threshold_optimizer.py # Capacity-constrained budget optimizer
│   └── train.py               # LightGBM model training with early stopping
├── tests/                     # Automated pytest test suites
│   └── test_features.py       # Deterministic unit tests for feature pipelines
├── .gitignore
├── README.md                  # Project overview, metrics & operational guide
└── requirements.txt           # Pinned production & development dependencies
```

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment:**
   Create a `.env` file in the root directory and add your OpenAI API key:
   ```env
   OPENAI_API_KEY="your-api-key-here"
   ```
3. **Run the Demo Pipeline:**
   ```bash
   python src/demo.py
   ```
   This will run an end-to-end simulation of the Guardian pipeline, passing mock orders through Stage 1 (LightGBM) and routing risky orders to Stage 2 (OpenAI).

4. **Run the Interactive Dashboard (Streamlit):**
   ```bash
   streamlit run src/dashboard.py
   ```
   This will launch a sleek web interface where you can manually tweak order parameters and see the Stage 1 & 2 risk engines react in real-time.

5. **Run the API Server (FastAPI):**
   ```bash
   python src/api.py
   ```
   This exposes the Guardian engine as a REST API on `localhost:8000/score_order`.

## Results & Metrics

Guardian was evaluated using a rigorous, leakage-free testing methodology:
- **Strict Data Isolation:** Thresholds were tuned strictly on the validation set, then locked and evaluated blindly on the holdout test set ($N = 2,000$).
- **Statistical Significance:** Lift confirmed via 1,000-resample bootstrap confidence intervals.

### 1. Stage 1 Model Performance (LightGBM)

| Model / Baseline | PR-AUC | Random Guess Baseline | 95% Bootstrap CI | Statistical Lift |
| :--- | :---: | :---: | :---: | :---: |
| **LightGBM Classifier** | **0.4147** | 0.3295 | **[0.3798, 0.4530]** | **+25.8% Lift ($p < 0.01$)** |

---

### 2. Operational Capacity Optimization (Picked on Val, Evaluated on Test)

Rather than unconstrained cost minimization (which trivially flagged 99.95% of orders due to heavy fraud penalties), Guardian optimizes for **real-world review team bandwidth**:

| Review Bandwidth (% of Total Volume) | Tuned Threshold | Test Flag Rate | Fraud Caught (Recall) | True Positives (TP) | False Positives (FP) | Operational Feasibility |
| :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **10%** | `0.5431` | 12.45% | 17.91% | 118 | 131 | Minimal manual review overhead |
| **20% (Target)** | **`0.5120`** | **21.30%** | **29.14%** | **192** | **234** | **Optimal ROI: Catches ~30% fraud in 20% team bandwidth** |
| **30%** | `0.4946` | 27.95% | 36.57% | 241 | 318 | Diminishing returns on review staff |

---

### 3. Economic Impact & Cost Matrix

| Classification Outcome | Real-World Scenario | Unit Financial Impact | Strategy / Mitigation |
| :--- | :--- | :---: | :--- |
| **True Positive (Caught Fraud)** | Risky COD intercepted & restricted | **+₹150 to ₹250 saved** | Avoids 2-way reverse logistics loss |
| **False Positive (Clean Flagged)** | Legitimate customer called for review | **-₹10 call cost** | Short 30s confirmation call preserves LTV |
| **False Negative (Missed Fraud)** | Order ships, customer refuses delivery | **-₹150 to ₹250 loss** | Merchant absorbs forward + RTO shipping |
| **True Negative (Safe Order)** | Clean order dispatched immediately | **₹0 marginal cost** | Instant friction-free checkout experience |

*(Note: These are illustrative cost estimates for this analysis, not measured or sourced figures from a specific merchant vendor.)*

---

### 4. Stage 2 LLM Alignment & The "Sample 14" Failure Recovery

| Experiment Phase | Test Samples | Agreement with Ground Truth | Failure Recovery Finding |
| :--- | :---: | :---: | :--- |
| Initial Prompt Version | 20 | 85% | Over-weighted 100% RTO on $n=1$ (Sample 14) into immediate `RESTRICT_COD` |
| **Calibrated Prompt (Final)** | **20** | **95%** | **Calibrated for sample size: properly downgraded to `VERIFY_MANUALLY`** |

**Documented Failure Case (Sample 14 - Order `ORD_0005721`):**
- **The Gap:** The initial LLM prompt saw a 100% historical RTO rate and triggered `RESTRICT_COD` without checking order volume. But the customer had only placed **one** past order ($n=1$). A 100% rate on one order is thin statistical evidence, not proof of fraud.
- **The Fix:** We rewrote the prompt with explicit statistical calibration instructions—instructing the model that $n=1$ warrants a soft `VERIFY_MANUALLY` touch, reserving hard restrictions for $n \ge 3$.


## Known Limitations

- **Synthetic Data Evaluation:** The dataset used in this project is fully synthetic, calibrated to a small number of published Indian e-commerce statistics (e.g., 25-40% fashion return rate, 20-40% COD RTO rate). Because no public dataset adequately captures COD and pincode-based RTO dynamics, we generated this data probabilistically. Consequently, the precision/recall numbers reflect how well our model learns these simulated patterns, and should not be taken as proof of exact real-world predictive performance.
