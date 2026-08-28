import pandas as pd

def temporal_split(df, test_size=0.2, val_size=0.1):
    """
    Splits the dataset strictly by time to prevent leakage.
    Simulates production environment: train on past, predict future.
    """
    df['order_date'] = pd.to_datetime(df['order_date'])
    df = df.sort_values('order_date').reset_index(drop=True)
    
    total_len = len(df)
    test_idx = int(total_len * (1 - test_size))
    val_idx = int(total_len * (1 - test_size - val_size))
    
    train = df.iloc[:val_idx]
    val = df.iloc[val_idx:test_idx]
    test = df.iloc[test_idx:]
    
    return train, val, test

if __name__ == "__main__":
    df = pd.read_csv('data/features.csv')
    train, val, test = temporal_split(df)
    
    train.to_csv('data/train.csv', index=False)
    val.to_csv('data/val.csv', index=False)
    test.to_csv('data/test.csv', index=False)
    
    print(f"Split complete. Train: {len(train)}, Val: {len(val)}, Test: {len(test)}")
