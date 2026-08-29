import pandas as pd
import numpy as np
import lightgbm as lgb

def calc_pr_auc(y_true, y_pred_prob):
    order = np.argsort(y_pred_prob)[::-1]
    y_true_sorted = y_true.iloc[order].values
    tp_cumsum = np.cumsum(y_true_sorted == 1)
    fp_cumsum = np.cumsum(y_true_sorted == 0)
    
    # Handle division by zero for precisions where tp_cumsum + fp_cumsum is 0
    den = tp_cumsum + fp_cumsum
    precisions = np.divide(tp_cumsum, den, out=np.zeros_like(tp_cumsum, dtype=float), where=den!=0)
    
    num_pos = np.sum(y_true == 1)
    recalls = np.divide(tp_cumsum, num_pos, out=np.zeros_like(tp_cumsum, dtype=float), where=num_pos!=0)
    
    precisions = np.concatenate([[1.0], precisions])
    recalls = np.concatenate([[0.0], recalls])
    return np.trapezoid(precisions, recalls)

if __name__ == "__main__":
    test = pd.read_csv('../data/test.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        test[c] = test[c].astype('category')
        
    bst = lgb.Booster(model_file='../models/stage1_lgbm.txt')
    test['lgbm_prob'] = bst.predict(test[features])
    
    n_iterations = 1000
    pr_aucs = []
    
    np.random.seed(42)
    n_size = len(test)
    
    print(f"Bootstrapping PR-AUC with {n_iterations} resamples...")
    
    for i in range(n_iterations):
        indices = np.random.randint(0, n_size, n_size)
        y_true_boot = test['is_bad_order'].iloc[indices]
        y_prob_boot = test['lgbm_prob'].iloc[indices]
        
        auc = calc_pr_auc(y_true_boot, y_prob_boot)
        pr_aucs.append(auc)
        
    pr_aucs = np.array(pr_aucs)
    lower = np.percentile(pr_aucs, 2.5)
    upper = np.percentile(pr_aucs, 97.5)
    mean_auc = np.mean(pr_aucs)
    
    print(f"Mean Bootstrapped PR-AUC: {mean_auc:.4f}")
    print(f"95% Confidence Interval: [{lower:.4f}, {upper:.4f}]")
