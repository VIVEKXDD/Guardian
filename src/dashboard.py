import streamlit as st
import pandas as pd
import lightgbm as lgb
import os
from dotenv import load_dotenv
from stage2_llm import LLMTriageAgent

# Page Config
st.set_page_config(page_title="Guardian AI Risk Manager", page_icon="🛡️", layout="wide")

# Load CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .allow { color: #00ff00; font-weight: bold; }
    .verify { color: #ffa500; font-weight: bold; }
    .restrict { color: #ff0000; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_guardian():
    load_dotenv()
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    with open('models/optimal_threshold.txt', 'r') as f:
        threshold = float(f.read().strip())
    agent = LLMTriageAgent(use_mock=False)
    return bst, threshold, agent

st.title("🛡️ Guardian AI Risk Manager")
st.markdown("A two-stage hybrid AI system to proactively mitigate RTO and Return fraud.")

bst, threshold, agent = load_guardian()

st.sidebar.header("Simulate New Order")
order_id = st.sidebar.text_input("Order ID", "ORD_DEMO_004")
payment_method = st.sidebar.selectbox("Payment Method", ["COD", "Prepaid"])
pincode_tier = st.sidebar.selectbox("Pincode Tier", ["Tier_1", "Tier_2", "Tier_3"])
category = st.sidebar.selectbox("Category", ["Fashion", "Footwear", "Electronics", "Home", "Beauty"])
order_value = st.sidebar.slider("Order Value (₹)", 100, 50000, 2500)
discount = st.sidebar.slider("Discount (%)", 0, 50, 0)

st.sidebar.subheader("Customer History")
past_orders = st.sidebar.number_input("Past Orders", 0, 50, 2)
past_returns = st.sidebar.number_input("Past Returns", 0, 50, 1)
past_rtos = st.sidebar.number_input("Past RTOs", 0, 50, 0)

past_return_rate = past_returns / past_orders if past_orders > 0 else 0.0
past_rto_rate = past_rtos / past_orders if past_orders > 0 else 0.0

if st.sidebar.button("Run Guardian Pipeline"):
    # 1. Prepare Data
    features = {
        'order_id': order_id,
        'payment_method': payment_method,
        'pincode_tier': pincode_tier,
        'category': category,
        'order_value': order_value,
        'discount_percent': discount,
        'past_order_count': past_orders,
        'past_return_count': past_returns,
        'past_rto_count': past_rtos,
        'past_return_rate': past_return_rate,
        'past_rto_rate': past_rto_rate
    }
    df = pd.DataFrame([features])
    for c in ['payment_method', 'pincode_tier', 'category']:
        df[c] = df[c].astype('category')
        
    model_features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    
    # 2. Stage 1 Execution
    with st.spinner("Stage 1: LightGBM Scoring..."):
        prob = float(bst.predict(df[model_features])[0])
        
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔍 Stage 1: ML Risk Scorer (LightGBM)")
        st.metric("Risk Probability", f"{prob:.4f}", delta=f"{prob - threshold:.4f} vs threshold", delta_color="inverse")
        st.progress(prob)
        
    with col2:
        st.subheader("🤖 Stage 2: LLM Triage (OpenAI)")
        
        if prob <= threshold:
            st.success("✅ DECISION: ALLOW (Stage 1 Auto-Approval)")
            st.info("Risk probability is below the operational capacity threshold. The order is automatically approved without requiring LLM triage.")
        else:
            st.warning("⚠️ FLAG: Order exceeds risk threshold. Routing to Stage 2...")
            with st.spinner("Stage 2: Gemini Triage Analysis..."):
                order_series = df.iloc[0]
                result = agent.triage_order(order_series)
                
                decision = result.get("decision", "ERROR")
                reasoning = result.get("reasoning", "Error")
                
                if decision == "ALLOW":
                    st.success(f"Final Decision: {decision}")
                elif decision == "VERIFY_MANUALLY":
                    st.warning(f"Final Decision: {decision}")
                else:
                    st.error(f"Final Decision: {decision}")
                    
                st.write("**LLM Reasoning:**")
                st.write(f"> *{reasoning}*")
