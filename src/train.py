import pandas as pd
import lightgbm as lgb
import os

def load_data():
    train = pd.read_csv('data/train.csv')
    val = pd.read_csv('data/val.csv')
    
    features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    target = 'is_bad_order'
    
    # Categoricals for LGBM
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        train[c] = train[c].astype('category')
        val[c] = val[c].astype('category')
        
    return train[features], train[target], val[features], val[target], cat_features

if __name__ == "__main__":
    X_train, y_train, X_val, y_val, cat_features = load_data()
    
    train_data = lgb.Dataset(X_train, label=y_train, categorical_feature=cat_features)
    val_data = lgb.Dataset(X_val, label=y_val, categorical_feature=cat_features, reference=train_data)
    
    params = {
        'objective': 'binary',
        'metric': 'auc',
        'learning_rate': 0.05,
        'num_leaves': 31,
        'random_state': 42
    }
    
    print("Training LightGBM model...")
    bst = lgb.train(
        params,
        train_data,
        num_boost_round=500,
        valid_sets=[train_data, val_data],
        callbacks=[lgb.early_stopping(stopping_rounds=20), lgb.log_evaluation(50)]
    )
    
    os.makedirs('models', exist_ok=True)
    bst.save_model('models/stage1_lgbm.txt')
    print("Model saved to models/stage1_lgbm.txt")
