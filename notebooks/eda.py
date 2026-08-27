import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda():
    data_path = '../data/synthetic_orders.csv'
    if not os.path.exists(data_path):
        print(f"Data file not found at {data_path}. Run data_generation.py first.")
        return

    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} orders.")
    
    # Basic info
    print("\n--- Basic Info ---")
    print(df.info())
    
    # 1. Overall Fraud / Abuse Stats
    print("\n--- Target Variables ---")
    print(df['is_bad_order'].value_counts(normalize=True))
    
    # 2. Return Rates by Category
    print("\n--- Return Rates by Category (Post-Delivery) ---")
    delivered = df[df['outcome'] != 'RTO']
    category_returns = delivered.groupby('category')['is_return'].mean().sort_values(ascending=False)
    print(category_returns)
    
    # 3. RTO Rates by Payment Method
    print("\n--- RTO Rates by Payment Method ---")
    payment_rto = df.groupby('payment_method')['is_rto'].mean()
    print(payment_rto)
    
    # 4. Pincode Tier vs RTO (COD only)
    print("\n--- COD RTO Rates by Pincode Tier ---")
    cod_orders = df[df['payment_method'] == 'COD']
    pincode_rto = cod_orders.groupby('pincode_tier')['is_rto'].mean().sort_values(ascending=False)
    print(pincode_rto)

    # Visualizations
    os.makedirs('../docs/plots', exist_ok=True)
    
    # Plot 1: RTO by Pincode Tier
    plt.figure(figsize=(8, 5))
    sns.barplot(data=cod_orders, x='pincode_tier', y='is_rto')
    plt.title('COD RTO Rate by Pincode Tier')
    plt.ylabel('RTO Probability')
    plt.savefig('../docs/plots/rto_by_pincode.png')
    plt.close()
    
    # Plot 2: Returns by Category
    plt.figure(figsize=(10, 5))
    sns.barplot(data=delivered, x='category', y='is_return')
    plt.title('Return Rate by Category (Post-delivery)')
    plt.ylabel('Return Probability')
    plt.savefig('../docs/plots/return_by_category.png')
    plt.close()

if __name__ == "__main__":
    run_eda()
