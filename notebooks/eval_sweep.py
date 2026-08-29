import pandas as pd
import numpy as np
import lightgbm as lgb
import json

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

def calc_pr_auc(y_true, y_pred_prob):
    # Sort descending
    order = np.argsort(y_pred_prob)[::-1]
    y_true_sorted = y_true.iloc[order].values
    
    tp_cumsum = np.cumsum(y_true_sorted == 1)
    fp_cumsum = np.cumsum(y_true_sorted == 0)
    
    precisions = tp_cumsum / (tp_cumsum + fp_cumsum)
    recalls = tp_cumsum / np.sum(y_true == 1)
    
    # Append (0,1) and (1,0) equivalent
    precisions = np.concatenate([[1.0], precisions])
    recalls = np.concatenate([[0.0], recalls])
    
    # Trapezoidal rule
    auc = np.trapezoid(precisions, recalls)
    return auc

if __name__ == "__main__":
    test = pd.read_csv('../data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='../models/stage1_lgbm.txt')
    test['lgbm_prob'] = bst.predict(test[features])
    
    # 1. Confusion Matrix Check at threshold 0.3
    print("--- 1. Confusion Matrix & Manual Metric Verification (Threshold 0.30) ---")
    m = calc_metrics(test['is_bad_order'], test['lgbm_prob'], threshold=0.30)
    tp, fp, fn, tn = m['TP'], m['FP'], m['FN'], m['TN']
    print(f"Raw Counts -> TP: {tp}, FP: {fp}, FN: {fn}, TN: {tn}")
    print(f"Manual Precision: {tp}/({tp}+{fp}) = {tp/(tp+fp):.4f} (Function says: {m['Precision']:.4f})")
    print(f"Manual Recall: {tp}/({tp}+{fn}) = {tp/(tp+fn):.4f} (Function says: {m['Recall']:.4f})")
    manual_f1 = 2 * (tp/(tp+fp) * tp/(tp+fn)) / (tp/(tp+fp) + tp/(tp+fn))
    print(f"Manual F1: {manual_f1:.4f} (Function says: {m['F1-Score']:.4f})")
    
    # 2. PR-AUC Calculation
    print("\n--- 2. PR-AUC (Average Precision) ---")
    base_rate = test['is_bad_order'].mean()
    pr_auc = calc_pr_auc(test['is_bad_order'], test['lgbm_prob'])
    print(f"No-skill baseline PR-AUC (base rate): {base_rate:.4f}")
    print(f"Model PR-AUC: {pr_auc:.4f}")
    print(f"Lift over no-skill: +{pr_auc - base_rate:.4f}")
    
    # 4. Threshold Sweep
    print("\n--- 4. Threshold Sweep ---")
    thresholds = [0.3, 0.4, 0.5, 0.6, 0.7]
    print(f"{'Threshold':<10} | {'Precision':<10} | {'Recall':<10} | {'F1-Score':<10}")
    print("-" * 50)
    for t in thresholds:
        met = calc_metrics(test['is_bad_order'], test['lgbm_prob'], threshold=t)
        print(f"{t:<10.1f} | {met['Precision']:<10.4f} | {met['Recall']:<10.4f} | {met['F1-Score']:<10.4f}")
        
    # 5. Always Predict Positive Baseline
    print("\n--- 5. Always Predict Positive Baseline ---")
    m_all_pos = calc_metrics(test['is_bad_order'], np.ones(len(test)), threshold=0.5)
    print(f"Precision: {m_all_pos['Precision']:.4f}")
    print(f"Recall: {m_all_pos['Recall']:.4f}")
    print(f"F1-Score: {m_all_pos['F1-Score']:.4f}")
