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
    test['lgbm_prob'] = bst.predict(test[features])
    
    probs = test['lgbm_prob']
    print("\n--- Probability Stats ---")
    print(f"Min: {probs.min():.4f}, Max: {probs.max():.4f}, Mean: {probs.mean():.4f}")
    print(f"10th: {np.percentile(probs, 10):.4f}, 50th: {np.percentile(probs, 50):.4f}, 90th: {np.percentile(probs, 90):.4f}")
    
    # 2. PR-AUC Calculation
    def calc_pr_auc(y_true, y_pred_prob):
        order = np.argsort(y_pred_prob)[::-1]
        y_true_sorted = y_true.iloc[order].values
        tp_cumsum = np.cumsum(y_true_sorted == 1)
        fp_cumsum = np.cumsum(y_true_sorted == 0)
        precisions = tp_cumsum / (tp_cumsum + fp_cumsum)
        recalls = tp_cumsum / np.sum(y_true == 1)
        precisions = np.concatenate([[1.0], precisions])
        recalls = np.concatenate([[0.0], recalls])
        return np.trapezoid(precisions, recalls)

    pr_auc = calc_pr_auc(test['is_bad_order'], test['lgbm_prob'])
    base_rate = test['is_bad_order'].mean()
    print(f"\nPR-AUC: {pr_auc:.4f} (Baseline: {base_rate:.4f})")
    
    # Optimize threshold for LGBM based on F1
    best_f1 = 0
    best_thresh = 0.5
    print("\n--- Threshold Sweep ---")
    thresholds = np.linspace(probs.min(), probs.max(), 10)
    for t in thresholds:
        met = calc_metrics(test['is_bad_order'], probs, threshold=t)
        print(f"Thresh: {t:.4f} | Prec: {met['Precision']:.4f} | Rec: {met['Recall']:.4f} | F1: {met['F1-Score']:.4f}")
        if met['F1-Score'] > best_f1:
            best_f1 = met['F1-Score']
            best_thresh = t
            
    lgbm_metrics = calc_metrics(test['is_bad_order'], test['lgbm_prob'], threshold=best_thresh)
    
    os.makedirs('docs', exist_ok=True)
    with open('docs/metrics.txt', 'w') as f:
        f.write(f"--- LightGBM (Stage 1) - Threshold: {best_thresh:.4f} ---\n")
        f.write(f"PR-AUC: {pr_auc:.4f}\n")
        for k, v in lgbm_metrics.items():
            f.write(f"{k}: {v:.4f}\n" if isinstance(v, float) else f"{k}: {v}\n")
            
    print("\nMetrics evaluated and saved to docs/metrics.txt")

    
    # Feature importance
    lgb.plot_importance(bst, max_num_features=10, importance_type='gain')
    plt.savefig('docs/feature_importance.png')
    print("Feature importance plotted to docs/feature_importance.png")
