import pandas as pd
import numpy as np

def generate_features(df):
    """
    Generates historical features for each order, ensuring NO DATA LEAKAGE.
    Calculations only consider orders placed strictly *before* the current order's timestamp.
    """
    # Ensure sorted chronologically
    df['order_date'] = pd.to_datetime(df['order_date'])
    df = df.sort_values(['customer_id', 'order_date']).reset_index(drop=True)
    
    # Customer Historical Features
    # Shift by 1 to exclude the current row from the expanding sum/count
    df['past_order_count'] = df.groupby('customer_id')['order_id'].cumcount()
    
    # Calculate cumulative sums for returns and RTOs, then shift
    df['cum_return'] = df.groupby('customer_id')['is_return'].cumsum()
    df['cum_rto'] = df.groupby('customer_id')['is_rto'].cumsum()
    
    df['past_return_count'] = df.groupby('customer_id')['cum_return'].shift(1).fillna(0)
    df['past_rto_count'] = df.groupby('customer_id')['cum_rto'].shift(1).fillna(0)
    
    # Rates
    df['past_return_rate'] = np.where(df['past_order_count'] > 0, df['past_return_count'] / df['past_order_count'], 0)
    df['past_rto_rate'] = np.where(df['past_order_count'] > 0, df['past_rto_count'] / df['past_order_count'], 0)
    
    # Cleanup temporary columns
    df = df.drop(columns=['cum_return', 'cum_rto'])
    
    # Re-sort by order_date
    df = df.sort_values('order_date').reset_index(drop=True)
    
    return df

if __name__ == "__main__":
    df = pd.read_csv('data/synthetic_orders.csv')
    df = generate_features(df)
    df.to_csv('data/features.csv', index=False)
    print(f"Features generated for {len(df)} orders. Saved to data/features.csv.")
