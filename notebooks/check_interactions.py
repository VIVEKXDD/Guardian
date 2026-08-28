import pandas as pd

df = pd.read_csv('../data/synthetic_orders.csv')

print(f"\n--- Overall Marginal is_bad_order Rate ---")
print(f"Total is_bad_order rate: {df['is_bad_order'].mean():.1%}")

print("\n--- Mean is_bad_order by (Payment Method x Pincode Tier x Category) ---")
interactions = df.groupby(['payment_method', 'pincode_tier', 'category'])['is_bad_order'].agg(['mean', 'count'])
# Filter for groups that have a meaningful sample size (e.g. > 10)
top_interactions = interactions[interactions['count'] > 10].sort_values(by='mean', ascending=False)
print(top_interactions.to_string())

# Check if any are above 75%
high_risk = top_interactions[top_interactions['mean'] > 0.75]
if not high_risk.empty:
    print("\nWARNING: The following interactions have >75% bad order rate (potential near-determinism):")
    print(high_risk)
else:
    print("\nSUCCESS: No interaction group (with n>10) has a bad order rate > 75%.")
