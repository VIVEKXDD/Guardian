# Issues and Resolutions

*Log of problems encountered during the build and how they were resolved.*

### 2026-08-27: Dataset Availability
- **Issue:** The ASOS GraphReturns dataset requires requesting access via OSF and lacks crucial Indian e-commerce specific features (COD, Pincode RTO).
- **Resolution:** Created a script to generate a synthetic dataset explicitly calibrated to public Indian market figures (25-40% return rates, 20-40% COD RTOs).

### 2026-08-30: Unconstrained Cost Optimization Trap
- **Issue:** When running unconstrained cost-curve optimization, the algorithm outputted a threshold near zero, flagging 99.95% of all orders. Because the financial loss of a missed fraud (₹150–₹250) mathematically dwarfs a ₹10 review phone call, unconstrained cost math dictates reviewing virtually everyone, making the ML filter useless.
- **Resolution:** Shifted the objective to **capacity-constrained optimization**. Fixed the manual review budget to a realistic 20% daily team bandwidth. Tuned the threshold on the validation set (`0.5120`) and evaluated blindly on the holdout test set, capturing **29.14% of total fraud** with verified bootstrap confidence intervals.

### 2026-09-01: LLM Sample-Size Calibration Failure (Sample 14)
- **Issue:** On Sample 14 (Order `ORD_0005721`), the Stage 2 LLM saw a historical 100% RTO rate and immediately issued a hard `RESTRICT_COD`. It failed to recognize that the sample size was exactly one past order ($n=1$), treating a single past event with the same confidence as a chronic fraudster with 10 orders.
- **Resolution:** Recalibrated the system prompt in `src/stage2_llm.py` with explicit statistical sample size guidelines. Instructed the model that $n=1$ is thin evidence warranting a lighter `VERIFY_MANUALLY` touch rather than a hard restriction, raising test cohort alignment to 95%.

