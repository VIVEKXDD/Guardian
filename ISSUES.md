# Issues and Resolutions

*Log of problems encountered during the build and how they were resolved.*

### 2026-08-27: Dataset Availability
- **Issue:** The ASOS GraphReturns dataset requires requesting access via OSF and lacks crucial Indian e-commerce specific features (COD, Pincode RTO).
- **Resolution:** Created a script to generate a synthetic dataset explicitly calibrated to public Indian market figures (25-40% return rates, 20-40% COD RTOs).
