import pandas as pd
import numpy as np

def rule_based_predict(df):
    """
    Baseline rule-based model:
    Predicts bad order if:
    - COD AND Tier_3
    - OR (Fashion OR Footwear) AND (past_return_rate > 0.5)
    """
    is_cod_tier3 = (df['payment_method'] == 'COD') & (df['pincode_tier'] == 'Tier_3')
    is_risky_cat = df['category'].isin(['Fashion', 'Footwear'])
    has_high_returns = df['past_return_rate'] > 0.5
    
    preds = is_cod_tier3 | (is_risky_cat & has_high_returns)
    return preds.astype(int)

if __name__ == "__main__":
    test = pd.read_csv('data/test.csv')
    test['baseline_pred'] = rule_based_predict(test)
    test[['order_id', 'is_bad_order', 'baseline_pred']].to_csv('data/baseline_preds.csv', index=False)
    print("Baseline predictions generated for test set.")
