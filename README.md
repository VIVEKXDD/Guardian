# Guardian - AI Risk Manager

**Guardian** is a two-stage AI risk engine designed to reduce merchant losses from returns and RTO (return-to-origin) fraud/abuse in Indian e-commerce.

## Problem Statement

Returns and RTOs represent a significant cost center in Indian e-commerce. 
- Fashion/footwear return rates run roughly 25–40%, particularly elevated during festive sales.
- COD (cash-on-delivery) RTO rates run roughly 20–40% depending on category and pincode.
Existing tooling is largely reactive (e.g., video proof for disputes). Guardian provides a **proactive** layer that scores return risk before an order ships, allowing merchants to take preventative measures without unnecessarily blocking honest customers.

## Architecture Summary

Guardian consists of two stages:
1. **Stage 1 (Pre-shipment Risk Scorer):** A LightGBM model that evaluates an order at placement (using customer history, product details, and geographic RTO rates) to output a risk tier (`allow` / `verify` / `restrict`).
2. **Stage 2 (Return-time Triage):** An LLM-based reasoning layer that evaluates return initiation reasons against historical patterns to route the return (`auto-approve refund` / `request evidence` / `flag for manual review`).

## Setup Instructions

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **Configure Environment:**
   Create a `.env` file in the root directory and add your Google Gemini API key:
   ```env
   GEMINI_API_KEY="your-api-key-here"
   ```
3. **Run the Demo Pipeline:**
   ```bash
   python src/demo.py
   ```
   This will run an end-to-end simulation of the Guardian pipeline, passing mock orders through Stage 1 (LightGBM) and routing risky orders to Stage 2 (Gemini/OpenAI).

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
- **Capacity Constrained Optimization:** Rather than unconstrained cost minimization (which incorrectly suggested flagging 99% of volume due to the massive cost penalty of fraud vs. manual review), Guardian employs a capacity budget constraint. At a **20% operational review budget**, the Stage 1 model successfully identifies and catches **29.14%** of all fraud.
- **Stage 2 LLM Alignment:** The Gemini-powered triage agent correctly reasons about complex risk edge cases (e.g., identifying that Prepaid payment mitigates the non-delivery risk of a past RTO), matching a human risk manager's ground-truth decisions on 95% of test samples.

## Known Limitations

- **Synthetic Data Evaluation:** The dataset used in this project is fully synthetic, calibrated to a small number of published Indian e-commerce statistics (e.g., 25-40% fashion return rate, 20-40% COD RTO rate). Because no public dataset adequately captures COD and pincode-based RTO dynamics, we generated this data probabilistically. Consequently, the precision/recall numbers reflect how well our model learns these simulated patterns, and should not be taken as proof of exact real-world predictive performance.
