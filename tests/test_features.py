import pandas as pd
import numpy as np
import pytest
from src.features import generate_features

def test_no_leakage_in_historical_features():
    """
    Test that the historical features (past_order_count, past_return_count)
    strictly DO NOT include the current row's data.
    """
    # Create dummy data for one customer
    data = pd.DataFrame({
        'order_id': ['O1', 'O2', 'O3', 'O4'],
        'customer_id': ['C1', 'C1', 'C1', 'C1'],
        'order_date': ['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04'],
        'is_return': [0, 1, 0, 1], # Customer returns order 2 and 4
        'is_rto': [0, 0, 1, 0]     # Customer RTOs order 3
    })
    
    res = generate_features(data)
    
    # Check past_order_count
    assert res['past_order_count'].tolist() == [0, 1, 2, 3]
    
    # Check past_return_count
    # Order 1: 0
    # Order 2: 0 (since order 1 didn't return)
    # Order 3: 1 (since order 2 returned)
    # Order 4: 1 (since order 3 didn't return)
    assert res['past_return_count'].tolist() == [0, 0, 1, 1]
    
    # Check past_rto_count
    # Order 1: 0
    # Order 2: 0
    # Order 3: 0
    # Order 4: 1 (since order 3 RTO'd)
    assert res['past_rto_count'].tolist() == [0, 0, 0, 1]

def test_multiple_customers():
    """
    Test that features reset and group correctly per customer.
    """
    data = pd.DataFrame({
        'order_id': ['O1', 'O2', 'O3'],
        'customer_id': ['C1', 'C2', 'C1'],
        'order_date': ['2023-01-01', '2023-01-02', '2023-01-03'],
        'is_return': [1, 0, 0],
        'is_rto': [0, 0, 0]
    })
    
    res = generate_features(data)
    
    c1_orders = res[res['customer_id'] == 'C1'].sort_values('order_date')
    c2_orders = res[res['customer_id'] == 'C2'].sort_values('order_date')
    
    # C1's second order should know about the first return
    assert c1_orders.iloc[1]['past_return_count'] == 1.0
    assert c1_orders.iloc[1]['past_order_count'] == 1.0
    
    # C2's first order should be 0
    assert c2_orders.iloc[0]['past_return_count'] == 0.0
    assert c2_orders.iloc[0]['past_order_count'] == 0.0
