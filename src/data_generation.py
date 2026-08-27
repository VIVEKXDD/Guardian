import pandas as pd
import numpy as np
import os
import random
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(num_orders=10000):
    print(f"Generating {num_orders} synthetic orders with probabilistic noise...")
    
    num_customers = int(num_orders * 0.6)
    customer_profiles = {
        f"CUST_{i:05d}": {
            'base_rto_risk': np.clip(np.random.normal(0.1, 0.2), 0, 0.8),
            'base_return_risk': np.clip(np.random.normal(0.15, 0.25), 0, 0.9)
        } for i in range(1, num_customers + 1)
    }
    customer_ids = list(customer_profiles.keys())
    
    categories = ['Fashion', 'Footwear', 'Electronics', 'Home', 'Beauty']
    cat_risk_mult = {'Fashion': 1.3, 'Footwear': 1.4, 'Electronics': 0.6, 'Home': 0.7, 'Beauty': 0.6}
    
    pincode_tiers = ['Tier_1', 'Tier_2', 'Tier_3']
    pin_rto_mult = {'Tier_1': 0.8, 'Tier_2': 1.1, 'Tier_3': 1.5}
    
    data = []
    start_date = datetime(2023, 1, 1)
    
    for i in range(num_orders):
        order_date = start_date + timedelta(days=np.random.randint(0, 365), hours=np.random.randint(0, 24))
        customer = random.choice(customer_ids)
        c_prof = customer_profiles[customer]
        
        category = np.random.choice(categories, p=[0.4, 0.2, 0.15, 0.15, 0.1])
        payment_method = np.random.choice(['COD', 'Prepaid'], p=[0.65, 0.35])
        pincode = np.random.choice(pincode_tiers, p=[0.3, 0.4, 0.3])
        
        order_value = np.random.exponential(scale=1500) + 300
        val_risk_mult = 1.2 if order_value > 5000 else 1.0
        
        discount_percent = np.random.uniform(0, 50)
        if order_date.month in [10, 11]:
            discount_percent += np.random.uniform(10, 20)
        discount_percent = min(discount_percent, 80)
        
        # Probabilistic RTO Calculation
        rto_logit = -2.0
        rto_logit += c_prof['base_rto_risk'] * 2.0
        if payment_method == 'COD':
            rto_logit += 1.5
        rto_logit += (pin_rto_mult[pincode] - 1.0) * 1.2
        rto_logit += np.random.normal(0, 1.3) # Noise increased
        
        rto_prob = 1 / (1 + np.exp(-rto_logit))
        is_rto = np.random.rand() < rto_prob
        
        # Probabilistic Return Calculation
        is_return = False
        return_reason = None
        if not is_rto:
            ret_logit = -1.5
            ret_logit += c_prof['base_return_risk'] * 2.5
            ret_logit += (cat_risk_mult[category] - 1.0) * 1.5
            ret_logit += (val_risk_mult - 1.0) * 0.8
            ret_logit += np.random.normal(0, 1.5) # Noise increased
            
            return_prob = 1 / (1 + np.exp(-ret_logit))
            is_return = np.random.rand() < return_prob
            
            if is_return:
                reasons = ['Wrong Size', 'Changed Mind', 'Defective', 'Not as Expected']
                return_reason = np.random.choice(reasons, p=[0.4, 0.3, 0.1, 0.2])
                
        outcome = 'RTO' if is_rto else ('Returned' if is_return else 'Delivered')
            
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
    df = df.sort_values('order_date').reset_index(drop=True)
    df['is_bad_order'] = df['is_rto'] | df['is_return']
    
    os.makedirs('data', exist_ok=True)
    df.to_csv('data/synthetic_orders.csv', index=False)
    
    print("\n--- Calibration Check ---")
    cod_orders = df[df['payment_method'] == 'COD']
    print(f"Overall COD rate: {len(cod_orders)/len(df):.1%}")
    print(f"COD RTO rate: {cod_orders['is_rto'].mean():.1%} (Target: 20-40%)")
    
    fashion = df[df['category'].isin(['Fashion', 'Footwear'])]
    fashion_ret = fashion[fashion['is_rto'] == 0]['is_return'].mean()
    print(f"Fashion Return rate (post-delivery): {fashion_ret:.1%} (Target: 25-40%)")
    
    print("\n--- Feature Correlation Sanity Check ---")
    check_df = df.copy()
    check_df['payment_COD'] = (check_df['payment_method'] == 'COD').astype(int)
    check_df['pincode_encoded'] = check_df['pincode_tier'].map({'Tier_1': 1, 'Tier_2': 2, 'Tier_3': 3})
    check_df['category_encoded'] = check_df['category'].astype('category').cat.codes
    
    cols_to_check = ['payment_COD', 'pincode_encoded', 'category_encoded', 'order_value', 'discount_percent']
    corrs = check_df[cols_to_check].corrwith(check_df['is_bad_order']).abs().sort_values(ascending=False)
    
    print("Absolute Pearson Correlation with 'is_bad_order':")
    for col, val in corrs.items():
        print(f"{col:<18}: {val:.3f}")
        if val > 0.8:
            print(f"  WARNING: {col} has dangerously high correlation (>0.8).")

if __name__ == "__main__":
    generate_synthetic_data()
