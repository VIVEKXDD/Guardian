# Design Decisions

*Append-only log of technical choices and the reasoning behind them.*

### 2026-08-27: Synthetic Dataset Generation
- **Decision:** Generate a synthetic dataset probabilistically, calibrated to published Indian e-commerce statistics (35% fashion returns, ~25% COD RTO rate).
- **Reasoning:** No public dataset captures the crucial COD and Pincode-level RTO dynamics of the Indian market. We explicitly inject random noise and base customer profiles so classes aren't perfectly separable. 
- **Limitation Acknowledgment:** This is a fully synthetic dataset. Our precision/recall numbers reflect how well the model learns our simulated probabilistic patterns, not definitive proof of real-world performance.

### 2026-08-27: Two-Stage Architecture
- **Decision:** Split the risk engine into a tabular ML pre-shipment scorer and an LLM post-return triage layer.
- **Reasoning:** A single tabular model cannot effectively parse free-text return reasons for nuanced fraud logic (e.g., "wrong size" claimed 5 times in a row). Conversely, an LLM is too slow and expensive to run on every placed order. The two-stage design optimizes for both cost and capability.
