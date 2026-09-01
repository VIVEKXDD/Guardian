import json
import os
import time
import pandas as pd
import numpy as np

try:
    import openai
except ImportError:
    openai = None

class LLMTriageAgent:
    def __init__(self, use_mock=False):
        self.use_mock = use_mock
        if not use_mock:
            if openai is None:
                raise ImportError("openai package is not installed.")
            # Map the user's specific env var name
            api_key = os.environ.get("Openai_API_KEY") or os.environ.get("OPENAI_API_KEY")
            self.client = openai.OpenAI(api_key=api_key)
        
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
- If return rate or RTO rate is very high (> 50%) and payment is COD, consider RESTRICT_COD.
- If return rate is moderate (e.g., 30-50%), use VERIFY_MANUALLY.
- If history is mostly clean or no history, use ALLOW.

CRITICAL INSTRUCTION ON SAMPLE SIZE:
- You MUST pay attention to `past_order_count` (the sample size, n).
- A 100% RTO rate on exactly 1 past order (n=1) is thin evidence. You should not overreact to n=1. It typically warrants a lighter VERIFY_MANUALLY touch rather than an outright restriction.
- A high RTO or return rate over multiple orders (e.g., n>=3) is strong evidence of a bad actor and justifies RESTRICT_COD if the current order is COD.

JSON Response:
"""

    def triage_order(self, order_series):
        prompt = self._generate_prompt(order_series)
        
        if self.use_mock:
            return {"decision": "ALLOW", "reasoning": "Mock fallback"}
        else:
            try:
                features = order_series.to_dict()
                response = self.client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": "You must respond with a valid JSON object."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.0
                )
                return json.loads(response.choices[0].message.content)
            except Exception as e:
                return {"reasoning": f"LLM Call Failed: {str(e)}", "decision": "ERROR"}

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test = pd.read_csv('data/test.csv')
    
    if "Openai_API_KEY" not in os.environ and "OPENAI_API_KEY" not in os.environ:
        print("WARNING: Openai_API_KEY not found in environment. Please export it to run the real LLM.")
        exit(1)
        
    agent = LLMTriageAgent(use_mock=False)
    
    print("--- Testing Stage 2 LLM Agent (OpenAI) on Samples 12-20 ---")
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
        
        # OpenAI limits are much higher than Gemini free tier, so 1 second is enough
        time.sleep(1)
