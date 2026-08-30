import pandas as pd
import numpy as np
import lightgbm as lgb
import os

def compute_metrics(y_true, probs, threshold):
    y_pred = (probs > threshold).astype(int)
    
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    
    flag_rate = (tp + fp) / len(y_true)
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    
    return {
        'threshold': threshold,
        'flag_rate': flag_rate,
        'recall': recall,
        'tp': tp, 'fp': fp, 'fn': fn, 'tn': tn
    }

if __name__ == "__main__":
    val = pd.read_csv('data/val.csv')
    test = pd.read_csv('data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        val[c] = val[c].astype('category')
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    
    val_probs = bst.predict(val[features])
    val_true = val['is_bad_order']
    
    test_probs = bst.predict(test[features])
    test_true = test['is_bad_order']
    
    thresholds = np.linspace(val_probs.min(), val_probs.max(), 500)
    val_results = [compute_metrics(val_true, val_probs, t) for t in thresholds]
    res_df = pd.DataFrame(val_results)
    
    budgets = [0.10, 0.20, 0.30]
    print("--- Constrained Threshold Optimization (Picked on Val, Applied to Test) ---")
    
    best_thresh_20 = None
    
    for b in budgets:
        valid = res_df[res_df['flag_rate'] <= b]
        if not valid.empty:
            best_val = valid.loc[valid['recall'].idxmax()]
        else:
            best_val = res_df.loc[(res_df['flag_rate'] - b).abs().idxmin()]
            
        opt_thresh = best_val['threshold']
        
        # Apply exactly this threshold to TEST
        test_met = compute_metrics(test_true, test_probs, opt_thresh)
        
        print(f"Budget: {b*100:.0f}% of Volume")
        print(f"  Threshold (from Val): {opt_thresh:.4f}")
        print(f"  Test Flag Rate: {test_met['flag_rate']*100:.2f}%")
        print(f"  Test Recall (Fraud Caught): {test_met['recall']*100:.2f}%")
        print(f"  Test TP: {test_met['tp']}, FP: {test_met['fp']}, FN: {test_met['fn']}")
        
        if b == 0.20:
            best_thresh_20 = opt_thresh
            
    # Save the selected threshold for the 20% budget
    os.makedirs('models', exist_ok=True)
    with open('models/optimal_threshold.txt', 'w') as f:
        f.write(str(best_thresh_20))
