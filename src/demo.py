import pandas as pd
import numpy as np
import lightgbm as lgb
import os
from dotenv import load_dotenv

# Ensure we can import from src if needed, though this is in src
from stage2_llm import LLMTriageAgent

# Load environment variables
load_dotenv()

def run_guardian_pipeline(order_data, customer_history):
    print("==================================================")
    print(f"📦 NEW ORDER RECEIVED: {order_data['order_id']}")
    print("==================================================")
    
    # 1. Combine into a single feature row
    features = {**order_data, **customer_history}
    df = pd.DataFrame([features])
    
    # 2. Preprocess (categorical conversions)
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        df[c] = df[c].astype('category')
        
    model_features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    
    # 3. Stage 1: LightGBM
    print("\n🔍 STAGE 1: ML Risk Scoring (LightGBM)")
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    prob = bst.predict(df[model_features])[0]
    
    # Load optimal threshold
    with open('models/optimal_threshold.txt', 'r') as f:
        threshold = float(f.read().strip())
        
    print(f"   Model Risk Probability: {prob:.4f}")
    print(f"   Operational Threshold:  {threshold:.4f}")
    
    if prob <= threshold:
        print("\n✅ DECISION: ALLOW (Stage 1 Auto-Approval)")
        return
        
    print("\n⚠️ FLAG: Order exceeds risk threshold. Routing to Stage 2.")
    
    # 4. Stage 2: LLM Triage
    print("\n🤖 STAGE 2: LLM Agent Triage (Gemini 3.6 Flash)")
    agent = LLMTriageAgent(use_mock=False)
    
    # Use the first row as a series
    order_series = df.iloc[0]
    result = agent.triage_order(order_series)
    
    print(f"\n   Final Decision: {result.get('decision', 'ERROR')}")
    print(f"   Reasoning:      {result.get('reasoning', 'ERROR')}")
    print("==================================================\n")

if __name__ == "__main__":
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY not found. Please setup your .env file.")
        exit(1)
        
    # Scenario A: Clean History
    scen_a_order = {
        'order_id': 'ORD_DEMO_001', 'payment_method': 'COD', 
        'pincode_tier': 'Tier_1', 'category': 'Fashion', 
        'order_value': 1500, 'discount_percent': 5
    }
    scen_a_hist = {
        'past_order_count': 5, 'past_return_count': 0, 'past_rto_count': 0,
        'past_return_rate': 0.0, 'past_rto_rate': 0.0
    }
    
    # Scenario B: High Risk (Serial Returner on COD)
    scen_b_order = {
        'order_id': 'ORD_DEMO_002', 'payment_method': 'COD', 
        'pincode_tier': 'Tier_3', 'category': 'Footwear', 
        'order_value': 4500, 'discount_percent': 20
    }
    scen_b_hist = {
        'past_order_count': 4, 'past_return_count': 3, 'past_rto_count': 1,
        'past_return_rate': 0.75, 'past_rto_rate': 0.25
    }

    # Scenario C: Moderate Risk (Prepaid mitigates it)
    scen_c_order = {
        'order_id': 'ORD_DEMO_003', 'payment_method': 'Prepaid', 
        'pincode_tier': 'Tier_2', 'category': 'Electronics', 
        'order_value': 12000, 'discount_percent': 10
    }
    scen_c_hist = {
        'past_order_count': 2, 'past_return_count': 1, 'past_rto_count': 0,
        'past_return_rate': 0.50, 'past_rto_rate': 0.0
    }

    run_guardian_pipeline(scen_a_order, scen_a_hist)
    import time
    time.sleep(15) # respect rate limit
    run_guardian_pipeline(scen_b_order, scen_b_hist)
    time.sleep(15)
    run_guardian_pipeline(scen_c_order, scen_c_hist)
