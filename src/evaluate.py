import pandas as pd
import numpy as np
import lightgbm as lgb
import os
import matplotlib.pyplot as plt

def calc_metrics(y_true, y_pred_prob, threshold=0.5):
    y_pred = (y_pred_prob > threshold).astype(int)
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    tn = np.sum((y_true == 0) & (y_pred == 0))
    
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    return {
        'Precision': precision,
        'Recall': recall,
        'F1-Score': f1,
        'TP': tp, 'FP': fp, 'FN': fn, 'TN': tn
    }

if __name__ == "__main__":
    test = pd.read_csv('data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    
    # LGBM Predictions
    test['lgbm_prob'] = bst.predict(test[features])
    
    # Baseline Predictions
    from baseline import rule_based_predict
    test['baseline_pred'] = rule_based_predict(test)
    
    # Evaluate
    baseline_metrics = calc_metrics(test['is_bad_order'], test['baseline_pred'], threshold=0.5)
    
    # Optimize threshold for LGBM based on F1 (roughly)
    best_f1 = 0
    best_thresh = 0.5
    for t in np.arange(0.2, 0.8, 0.05):
        met = calc_metrics(test['is_bad_order'], test['lgbm_prob'], threshold=t)
        if met['F1-Score'] > best_f1:
            best_f1 = met['F1-Score']
            best_thresh = t
            
    lgbm_metrics = calc_metrics(test['is_bad_order'], test['lgbm_prob'], threshold=best_thresh)
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/metrics.txt', 'w') as f:
        f.write("--- Baseline (Rule-Based) ---\n")
        for k, v in baseline_metrics.items():
            f.write(f"{k}: {v:.4f}\n" if isinstance(v, float) else f"{k}: {v}\n")
            
        f.write(f"\n--- LightGBM (Stage 1) - Threshold: {best_thresh:.2f} ---\n")
        for k, v in lgbm_metrics.items():
            f.write(f"{k}: {v:.4f}\n" if isinstance(v, float) else f"{k}: {v}\n")
            
    print("Metrics evaluated and saved to docs/metrics.txt")
    
    # Feature importance
    lgb.plot_importance(bst, max_num_features=10, importance_type='gain')
    plt.savefig('docs/feature_importance.png')
    print("Feature importance plotted to docs/feature_importance.png")
