# Data Notes

This document describes the data strategy for Guardian.

## Data Source
We use a **synthetic dataset** generated specifically for this project, calibrated to mirror published statistics of the Indian e-commerce landscape.

## Calibration Statistics
- **Overall Fashion Return Rate:** Calibrated to roughly 25-40%.
- **COD RTO Rate:** Calibrated to roughly 20-40%, dependent on geographic features (pincode tier).
- **Fraud/Abuse Patterns:** Injected specific patterns where certain customer IDs exhibit unusually high return rates or conflicting return reasons.

## Train / Validation / Test Split
- **Strategy:** The data will be split temporally (or by customer ID) to prevent data leakage. We will **never** perform a random row-level split, as this would leak a customer's future behavior into the training set, artificially inflating model performance.

---
> **Note:** As of the `data-v1-final` commit, this is the frozen dataset version all Stage 1 modeling is built on. Regenerating after this point requires re-running the full leakage/interaction/split checks.
