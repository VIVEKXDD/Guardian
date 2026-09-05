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
- **Data Leakage Prevention:** Model evaluation was strictly isolated. Thresholds for the Stage 1 model were selected solely on the validation set, and then applied blindly to the holdout test set to ensure realistic operational metrics.
- **Stage 1 Performance:** The LightGBM model achieves a **PR-AUC of 0.4147**, a statistically significant lift over the 0.3295 random-guess baseline (confirmed via 1,000-resample bootstrap CI: [0.3798, 0.4530]).

### The Cost Table (Capacity-Constrained Optimization)
Rather than unconstrained cost minimization (which incorrectly suggested flagging 99% of volume due to the massive cost penalty of fraud vs. manual review), Guardian employs a **capacity budget constraint**. 

**The Economic Reality (FP vs FN Costs):**
- **Cost of a False Negative (Missed Fraud):** ~₹150 for an RTO (forward & reverse logistics) or ~₹250 for a Return (shipping + QC).
- **Cost of a False Positive (Flagging a Good Order):** ~₹10 for a manual verification call. Because the friction is low, traditional cost-sensitive learning algorithms aggressively flag everything, which doesn't scale operationally.
*(Note: These are illustrative cost estimates for this analysis, not measured or sourced figures from a specific vendor.)*

To solve this, we assume a manual review team can only handle calling the top 20% of orders daily:
- **Operational Threshold:** `0.5120` risk probability.
- **Fraud Caught:** **29.14%** of all fraudulent/RTO orders are intercepted within that 20% bandwidth.
- **Impact:** By focusing the 20% operational budget purely on the highest-risk segment prioritized by LightGBM, the business maximizes loss-prevention ROI without expanding headcount.

### Stage 2 LLM Alignment & The "Sample 14" Failure Case
The OpenAI-powered triage agent successfully matches a human risk manager's ground-truth decisions on 95% of test samples. However, evaluating the failures is critical for AI transparency.

**The Failure Case (Sample 14):** 
In early prompt iterations, the LLM evaluated an order with 1 past RTO out of 1 past order (100% RTO rate) and immediately returned `RESTRICT_COD`. 
- **The Gap:** The LLM failed to reason about *sample size (n=1)*. A 100% RTO rate on a single order is thin evidence compared to 3 RTOs out of 4 orders, and should warrant a softer `VERIFY_MANUALLY` touch rather than a hard restriction. 
- **The Fix:** We updated the system prompt to explicitly instruct the LLM on calibrated confidence for thin histories, restoring human-like nuance to the decision engine.

## Known Limitations

- **Synthetic Data Evaluation:** The dataset used in this project is fully synthetic, calibrated to a small number of published Indian e-commerce statistics (e.g., 25-40% fashion return rate, 20-40% COD RTO rate). Because no public dataset adequately captures COD and pincode-based RTO dynamics, we generated this data probabilistically. Consequently, the precision/recall numbers reflect how well our model learns these simulated patterns, and should not be taken as proof of exact real-world predictive performance.
