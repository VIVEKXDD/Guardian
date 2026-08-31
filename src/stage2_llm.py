import json
import os
import time
import pandas as pd
import numpy as np

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

class LLMTriageAgent:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        if not use_mock:
            if genai is None:
                raise ImportError("google-genai is not installed.")
            self.client = genai.Client()
        
    def _generate_prompt(self, order_series):
        """Constructs the prompt for the LLM."""
        return f"""
You are an AI Risk Manager for an e-commerce platform.
Please review the following flagged order and determine the appropriate action.

[Customer History]
Past Orders: {order_series['past_order_count']}
Past Returns: {order_series['past_return_count']}
Past RTOs: {order_series['past_rto_count']}

[Current Order]
Order Value: {order_series['order_value']}
Discount: {order_series['discount_percent']}%
Category: {order_series['category']}
Payment Method: {order_series['payment_method']}
Pincode Tier: {order_series['pincode_tier']}

Based on the customer's historical patterns and current order traits, output a JSON object with:
1. "reasoning": A brief explanation of your decision.
2. "decision": One of ["ALLOW", "VERIFY_MANUALLY", "RESTRICT_COD"]

RULES:
- If return rate or RTO rate is very high (> 50%) and payment is COD, use RESTRICT_COD.
- If return rate is moderate (e.g., 30-50%), use VERIFY_MANUALLY.
- If history is mostly clean or no history, use ALLOW.

JSON Response:
"""

    def triage_order(self, order_series):
        prompt = self._generate_prompt(order_series)
        
        if self.use_mock:
            return {"decision": "ALLOW", "reasoning": "Mock fallback"}
        else:
            try:
                response = self.client.models.generate_content(
                    model='gemini-3.6-flash',
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        temperature=0.0
                    ),
                )
                return json.loads(response.text)
            except Exception as e:
                return {"reasoning": f"LLM Call Failed: {str(e)}", "decision": "ERROR"}

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test = pd.read_csv('data/test.csv')
    
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY not found in environment. Please export GEMINI_API_KEY to run the real LLM.")
        exit(1)
        
    agent = LLMTriageAgent(use_mock=False)
    
    print("--- Testing Stage 2 LLM Agent (Gemini) on Samples 12-20 ---")
    np.random.seed(42)
    # Grab the same 20 indices, but only process the last 9
    sample_indices = np.random.choice(test.index, 20, replace=False)[11:]
    
    for i, idx in enumerate(sample_indices):
        order = test.loc[idx]
        print(f"\n[Sample {i+12}] Order ID {order['order_id']}")
        print(f"Features: Prev Returns: {order['past_return_count']}/{order['past_order_count']} | Prev RTOs: {order['past_rto_count']}/{order['past_order_count']} | {order['payment_method']} | {order['category']}")
        
        res = agent.triage_order(order)
        print(f"Decision: {res.get('decision', 'ERROR')}")
        print(f"Reasoning: {res.get('reasoning', 'ERROR')}")
        
        # Google GenAI Free Tier has a strict 5 Requests Per Minute (RPM) limit.
        # 60 seconds / 5 requests = 12 seconds per request. We use 15 to be safe.
        time.sleep(15)
