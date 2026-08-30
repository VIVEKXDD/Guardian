import pandas as pd
import numpy as np
import lightgbm as lgb
import os

def compute_cost(y_true, probs, threshold, cost_fn, cost_fp):
    y_pred = (probs > threshold).astype(int)
    
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    
    total_cost = (fn * cost_fn) + (fp * cost_fp)
    flag_rate = (tp + fp) / len(y_true)
    
    return {
        'threshold': threshold,
        'total_cost': total_cost,
        'fn_cost': fn * cost_fn,
        'fp_cost': fp * cost_fp,
        'flag_rate': flag_rate,
        'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn
    }

if __name__ == "__main__":
    test = pd.read_csv('data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    probs = bst.predict(test[features])
    y_true = test['is_bad_order']
    
    COST_FN = 100
    COST_FP = 5
    
    thresholds = np.linspace(probs.min(), probs.max(), 100)
    results = []
    for t in thresholds:
        results.append(compute_cost(y_true, probs, t, COST_FN, COST_FP))
        
    res_df = pd.DataFrame(results)
    best = res_df.loc[res_df['total_cost'].idxmin()]
    
    print("--- Cost-Based Threshold Optimization ---")
    print(f"Cost of FN (Missed Fraud): {COST_FN}")
    print(f"Cost of FP (Stage 2 Review): {COST_FP}")
    print(f"\nOptimal Threshold: {best['threshold']:.4f}")
    print(f"Total Expected Cost: {best['total_cost']}")
    print(f"Flag Rate: {best['flag_rate']*100:.2f}% of orders sent to Stage 2")
    print(f"TP: {best['tp']}, FP: {best['fp']}, FN: {best['fn']}, TN: {best['tn']}")
    
    # Save the selected threshold
    os.makedirs('models', exist_ok=True)
    with open('models/optimal_threshold.txt', 'w') as f:
        f.write(str(best['threshold']))
