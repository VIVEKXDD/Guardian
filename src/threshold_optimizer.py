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
    test = pd.read_csv('data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    probs = bst.predict(test[features])
    y_true = test['is_bad_order']
    
    thresholds = np.linspace(probs.min(), probs.max(), 500)
    results = [compute_metrics(y_true, probs, t) for t in thresholds]
    res_df = pd.DataFrame(results)
    
    # Constrained Optimization: Maximize recall for a given budget
    budgets = [0.10, 0.20, 0.30]
    print("--- Constrained Threshold Optimization (Capacity Budgeting) ---")
    
    best_thresh_20 = None
    
    for b in budgets:
        valid = res_df[res_df['flag_rate'] <= b]
        if not valid.empty:
            best = valid.loc[valid['recall'].idxmax()]
        else:
            best = res_df.loc[(res_df['flag_rate'] - b).abs().idxmin()]
            
        print(f"Budget: {b*100:.0f}% of Volume")
        print(f"  Threshold: {best['threshold']:.4f}")
        print(f"  Actual Flag Rate: {best['flag_rate']*100:.2f}%")
        print(f"  Recall (Fraud Caught): {best['recall']*100:.2f}%")
        print(f"  TP: {best['tp']}, FP: {best['fp']}, FN: {best['fn']}")
        
        if b == 0.20:
            best_thresh_20 = best['threshold']
            
    # Save the selected threshold for the 20% budget
    os.makedirs('models', exist_ok=True)
    with open('models/optimal_threshold.txt', 'w') as f:
        f.write(str(best_thresh_20))
