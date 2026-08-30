import json

class LLMTriageAgent:
    def __init__(self, use_mock=True):
        self.use_mock = use_mock
        
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

JSON Response:
"""

    def triage_order(self, order_series):
        prompt = self._generate_prompt(order_series)
        
        if self.use_mock:
            # Simple mock heuristic based on the data
            if order_series['past_return_rate'] > 0.6 and order_series['payment_method'] == 'COD':
                return {
                    "reasoning": "High historical return rate combined with COD payment. High risk of RTO.",
                    "decision": "RESTRICT_COD"
                }
            elif order_series['past_return_rate'] > 0.4:
                return {
                    "reasoning": "Moderate historical return rate. Requires manual verification.",
                    "decision": "VERIFY_MANUALLY"
                }
            else:
                return {
                    "reasoning": "Order flagged by Stage 1, but historical context looks acceptable.",
                    "decision": "ALLOW"
                }
        else:
            # Here we would integrate with an actual LLM API
            raise NotImplementedError("Real LLM integration not yet implemented. Use use_mock=True.")

if __name__ == "__main__":
    import pandas as pd
    import numpy as np
    test = pd.read_csv('data/test.csv')
    
    agent = LLMTriageAgent(use_mock=True)
    
    # Test on a realistic sample set
    print("--- Testing Stage 2 LLM Agent (Mock) on 20 Samples ---")
    
    # Pick 20 samples representing a mix of safe and risky orders
    np.random.seed(42)
    sample_indices = np.random.choice(test.index, 20, replace=False)
    
    for i, idx in enumerate(sample_indices):
        order = test.loc[idx]
        res = agent.triage_order(order)
        print(f"\n[Sample {i+1}] Order ID {order['order_id']}")
        print(f"Features: Prev Returns: {order['past_return_count']} | Prev RTOs: {order['past_rto_count']} | {order['payment_method']} | {order['category']}")
        print(f"Decision: {res['decision']}")
        print(f"Reasoning: {res['reasoning']}")
