import pandas as pd
import numpy as np

df = pd.read_csv('../data/features.csv')

print("--- Correlation of Historical Features with is_bad_order ---")
# Discretize historical features to see if any bucket becomes deterministic
df['past_rto_bucket'] = pd.cut(df['past_rto_count'], bins=[-1, 0, 1, 3, 10], labels=['0', '1', '2-3', '4+'])
df['past_return_bucket'] = pd.cut(df['past_return_count'], bins=[-1, 0, 1, 3, 10], labels=['0', '1', '2-3', '4+'])

print("\nMean is_bad_order by Past RTO Count Bucket:")
print(df.groupby('past_rto_bucket')['is_bad_order'].agg(['mean', 'count']))

print("\nMean is_bad_order by Past Return Count Bucket:")
print(df.groupby('past_return_bucket')['is_bad_order'].agg(['mean', 'count']))

print("\n--- Interaction: Payment Method x Tier x Past Return Bucket ---")
interactions = df.groupby(['payment_method', 'pincode_tier', 'past_return_bucket'])['is_bad_order'].agg(['mean', 'count'])
top_interactions = interactions[interactions['count'] > 10].sort_values(by='mean', ascending=False)
print(top_interactions.head(15))

high_risk = top_interactions[top_interactions['mean'] > 0.85] # Allow slightly higher threshold for deep historical cuts
if not high_risk.empty:
    print("\nWARNING: Found near-deterministic historical interaction (>85% bad order rate):")
    print(high_risk)
else:
    print("\nSUCCESS: Historical interactions remain probabilistic (no group >85%).")
