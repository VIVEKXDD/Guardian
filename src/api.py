from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pandas as pd
import lightgbm as lgb
from dotenv import load_dotenv
import os

from stage2_llm import LLMTriageAgent

# Load environment variables
load_dotenv()

app = FastAPI(title="Guardian AI Risk Manager API", version="1.0")

# Global models (loaded at startup)
bst = None
threshold = 0.5120
agent = None

@app.on_event("startup")
def load_models():
    global bst, threshold, agent
    print("Loading Stage 1 LightGBM Model...")
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    
    with open('models/optimal_threshold.txt', 'r') as f:
        threshold = float(f.read().strip())
        
    print("Initializing Stage 2 LLM Agent (OpenAI)...")
    agent = LLMTriageAgent(use_mock=False)

class OrderRequest(BaseModel):
    order_id: str
    payment_method: str
    pincode_tier: str
    category: str
    order_value: float
    discount_percent: float
    past_order_count: int
    past_return_count: int
    past_rto_count: int
    past_return_rate: float
    past_rto_rate: float

@app.post("/score_order")
def score_order(order: OrderRequest):
    # Convert Pydantic model to dict
    features = order.dict()
    df = pd.DataFrame([features])
    
    # Preprocess categorical features
    cat_features = ['payment_method', 'pincode_tier', 'category']
    for c in cat_features:
        df[c] = df[c].astype('category')
        
    model_features = [
        'payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 
        'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate'
    ]
    
    # Stage 1: LightGBM
    prob = float(bst.predict(df[model_features])[0])
    
    response = {
        "order_id": order.order_id,
        "stage1_risk_probability": prob,
        "threshold": threshold,
    }
    
    # If below threshold, Auto-Approve
    if prob <= threshold:
        response["final_decision"] = "ALLOW"
        response["reasoning"] = "Stage 1 Auto-Approval (Below Risk Threshold)"
        return response
        
    # Stage 2: LLM Triage
    order_series = df.iloc[0]
    try:
        llm_result = agent.triage_order(order_series)
        response["final_decision"] = llm_result.get("decision", "ERROR")
        response["reasoning"] = llm_result.get("reasoning", "LLM parsing failed")
    except Exception as e:
        response["final_decision"] = "ERROR"
        response["reasoning"] = f"LLM Call Failed: {str(e)}"
        
    return response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
