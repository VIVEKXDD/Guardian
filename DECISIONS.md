# Design Decisions

*Append-only log of technical choices and the reasoning behind them.*

### 2026-08-27: Synthetic Dataset Generation
- **Decision:** Generate a synthetic dataset calibrated to Indian e-commerce statistics instead of attempting to use the ASOS GraphReturns dataset natively.
- **Reasoning:** The ASOS dataset lacks Indian market specific features crucial to our problem statement (e.g., COD vs Prepaid, Pincode RTO rates). Generating calibrated synthetic data allows us to properly model and evaluate the specific fraud vectors we are defending against.

### 2026-08-27: Two-Stage Architecture
- **Decision:** Split the risk engine into a tabular ML pre-shipment scorer and an LLM post-return triage layer.
- **Reasoning:** A single tabular model cannot effectively parse free-text return reasons for nuanced fraud logic (e.g., "wrong size" claimed 5 times in a row). Conversely, an LLM is too slow and expensive to run on every placed order. The two-stage design optimizes for both cost and capability.
