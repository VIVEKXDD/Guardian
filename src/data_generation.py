import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(num_orders=10000):
    """
    Generates a synthetic e-commerce dataset calibrated to Indian market statistics:
    - 25-40% return rate for fashion
    - 20-40% COD RTO rate
    """
    print(f"Generating {num_orders} synthetic orders...")
    
    # Base data
    customer_ids = [f"CUST_{i:05d}" for i in range(1, int(num_orders * 0.6))] # Some repeat customers
    categories = ['Fashion', 'Footwear', 'Electronics', 'Home', 'Beauty']
    pincode_tiers = ['Tier_1', 'Tier_2', 'Tier_3']
    
    data = []
    
    # Generate temporal base
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_orders):
        # Order timestamp
        order_date = start_date + timedelta(days=np.random.randint(0, 365), hours=np.random.randint(0, 24))
        
        # Customer
        customer = random.choice(customer_ids)
        
        # Product Category
        category = np.random.choice(categories, p=[0.4, 0.2, 0.15, 0.15, 0.1]) # Fashion heavy
        
        # Payment Method
        payment_method = np.random.choice(['COD', 'Prepaid'], p=[0.65, 0.35]) # India is COD heavy
        
        # Pincode Tier
        pincode = np.random.choice(pincode_tiers, p=[0.3, 0.4, 0.3])
        
        # Order Value & Discount
        order_value = np.random.exponential(scale=1500) + 300
        discount_percent = np.random.uniform(0, 50)
        if order_date.month in [10, 11]: # Festive season proxy
            discount_percent += np.random.uniform(10, 20)
            
        discount_percent = min(discount_percent, 80) # Cap at 80%
        
        # --- Injecting Fraud / Return Logic ---
        
        # Base RTO logic for COD
        rto_prob = 0.02
        if payment_method == 'COD':
            if pincode == 'Tier_3':
                rto_prob = 0.35
            elif pincode == 'Tier_2':
                rto_prob = 0.25
            else:
                rto_prob = 0.15
        
        # Base Return logic (Post-delivery)
        return_prob = 0.05
        if category in ['Fashion', 'Footwear']:
            return_prob = 0.35
            
        # Is this an RTO? (Return to origin before delivery)
        is_rto = np.random.rand() < rto_prob
        
        # Is this a Return? (Customer returns after delivery)
        # Cannot be a return if it's already an RTO
        is_return = False
        return_reason = None
        if not is_rto:
            is_return = np.random.rand() < return_prob
            if is_return:
                reasons = ['Wrong Size', 'Changed Mind', 'Defective', 'Not as Expected']
                return_reason = np.random.choice(reasons, p=[0.4, 0.3, 0.1, 0.2])
                
        # Outcome
        outcome = 'Delivered'
        if is_rto:
            outcome = 'RTO'
        elif is_return:
            outcome = 'Returned'
            
        data.append({
            'order_id': f"ORD_{i:07d}",
            'customer_id': customer,
            'order_date': order_date,
            'category': category,
            'payment_method': payment_method,
            'pincode_tier': pincode,
            'order_value': round(order_value, 2),
            'discount_percent': round(discount_percent, 2),
            'is_rto': int(is_rto),
            'is_return': int(is_return),
            'outcome': outcome,
            'return_reason': return_reason
        })
        
    df = pd.DataFrame(data)
    
    # Calculate historical features (simulate what we know AT order placement time)
    # We must sort by time to prevent leakage
    df = df.sort_values('order_date').reset_index(drop=True)
    
    # Create target variable: 1 if RTO or Return, 0 otherwise
    df['is_bad_order'] = df['is_rto'] | df['is_return']
    
    # Save the raw dataset
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_orders.csv', index=False)
    print("Dataset generated and saved to data/synthetic_orders.csv")
    
    # Print calibration stats
    print("\n--- Calibration Check ---")
    print(f"Overall COD rate: {(df['payment_method'] == 'COD').mean():.1%}")
    cod_rto = df[df['payment_method'] == 'COD']['is_rto'].mean()
    print(f"COD RTO rate: {cod_rto:.1%} (Target: 20-40%)")
    
    fashion = df[df['category'].isin(['Fashion', 'Footwear'])]
    fashion_ret = fashion[fashion['is_rto'] == 0]['is_return'].mean()
    print(f"Fashion Return rate (post-delivery): {fashion_ret:.1%} (Target: 25-40%)")

if __name__ == "__main__":
    generate_synthetic_data()
