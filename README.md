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

TBD

## Results & Metrics

TBD

## Known Limitations

- **Synthetic Data Evaluation:** The dataset used in this project is fully synthetic, calibrated to a small number of published Indian e-commerce statistics (e.g., 25-40% fashion return rate, 20-40% COD RTO rate). Because no public dataset adequately captures COD and pincode-based RTO dynamics, we generated this data probabilistically. Consequently, the precision/recall numbers reflect how well our model learns these simulated patterns, and should not be taken as proof of exact real-world predictive performance.
