import pandas as pd

df = pd.read_csv('data/synthetic_orders.csv')

print("--- Mean is_bad_order by Pincode Tier ---")
print(df.groupby('pincode_tier')['is_bad_order'].mean().sort_values(ascending=False))

print("\n--- Mean is_bad_order by Category ---")
print(df.groupby('category')['is_bad_order'].mean().sort_values(ascending=False))

print("\n--- Mean is_bad_order by (Payment Method x Pincode Tier x Category) ---")
interactions = df.groupby(['payment_method', 'pincode_tier', 'category'])['is_bad_order'].agg(['mean', 'count'])
# Filter for groups that have a meaningful sample size (e.g. > 10) and show top
top_interactions = interactions[interactions['count'] > 10].sort_values(by='mean', ascending=False)
print(top_interactions.head(15))

# Check if any are above 75%
high_risk = top_interactions[top_interactions['mean'] > 0.75]
if not high_risk.empty:
    print("\nWARNING: The following interactions have >75% bad order rate (potential near-determinism):")
    print(high_risk)
else:
    print("\nSUCCESS: No interaction group (with n>10) has a bad order rate > 75%.")
