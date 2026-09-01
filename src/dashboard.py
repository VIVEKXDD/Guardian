import streamlit as st
import pandas as pd
import lightgbm as lgb
import os
import time
from dotenv import load_dotenv
from stage2_llm import LLMTriageAgent
import json

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Guardian Risk Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# CUSTOM CSS FOR PREMIUM AESTHETICS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Sleek gradient header */
    .premium-header {
        background: linear-gradient(90deg, #1E293B 0%, #0F172A 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
        border-left: 5px solid #3B82F6;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .premium-header h1 {
        margin: 0;
        font-weight: 700;
        letter-spacing: -0.5px;
        color: #F8FAFC;
    }
    
    .premium-header p {
        margin: 0.5rem 0 0 0;
        color: #94A3B8;
        font-size: 1.1rem;
    }

    /* Metric Cards */
    .stMetric {
        background-color: #1E293B;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    /* Status Badges */
    .badge-allow {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #10B981;
        font-weight: 600;
        font-size: 1.2rem;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    
    .badge-verify {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #F59E0B;
        font-weight: 600;
        font-size: 1.2rem;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    
    .badge-restrict {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #EF4444;
        font-weight: 600;
        font-size: 1.2rem;
        display: inline-block;
        width: 100%;
        text-align: center;
    }
    
    /* Reasoning Box */
    .reasoning-box {
        background-color: #0F172A;
        border-left: 4px solid #6366F1;
        padding: 20px;
        border-radius: 0 8px 8px 0;
        color: #E2E8F0;
        font-size: 1.05rem;
        line-height: 1.6;
        margin-top: 15px;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# LOAD MODELS (CACHED)
# ==========================================
@st.cache_resource
def load_guardian():
    load_dotenv()
    bst = lgb.Booster(model_file='models/stage1_lgbm.txt')
    with open('models/optimal_threshold.txt', 'r') as f:
        threshold = float(f.read().strip())
    agent = LLMTriageAgent(use_mock=False)
    return bst, threshold, agent

bst, threshold, agent = load_guardian()

# ==========================================
# MAIN LAYOUT
# ==========================================
st.markdown("""
<div class="premium-header">
    <h1>🛡️ Guardian Enterprise Engine</h1>
    <p>Real-time Hybrid ML + LLM Fraud Mitigation</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR (CONTROL PANEL)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
    st.markdown("### 🎛️ Simulation Controls")
    st.markdown("Inject mock webhook data into the Guardian API.")
    
    st.divider()
    
    st.markdown("#### 📦 Order Details")
    order_id = st.text_input("Order ID", "ORD_9999201")
    col_pm, col_tier = st.columns(2)
    with col_pm:
        payment_method = st.selectbox("Payment", ["COD", "Prepaid"])
    with col_tier:
        pincode_tier = st.selectbox("Tier", ["Tier_1", "Tier_2", "Tier_3"], index=2)
        
    col_cat, col_val = st.columns(2)
    with col_cat:
        category = st.selectbox("Category", ["Fashion", "Footwear", "Electronics", "Home", "Beauty"])
    with col_val:
        order_value = st.number_input("Value (₹)", value=4500, step=100)
    
    discount = st.slider("Discount Applied (%)", 0, 50, 20)
    
    st.divider()
    
    st.markdown("#### 👤 Historical CRM Data")
    past_orders = st.number_input("Total Past Orders", 0, 100, 4)
    col_ret, col_rto = st.columns(2)
    with col_ret:
        past_returns = st.number_input("Past Returns", 0, past_orders, 3)
    with col_rto:
        past_rtos = st.number_input("Past RTOs", 0, past_orders, 1)

past_return_rate = past_returns / past_orders if past_orders > 0 else 0.0
past_rto_rate = past_rtos / past_orders if past_orders > 0 else 0.0

# Build Feature Dictionary
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

# ==========================================
# EXECUTION DASHBOARD
# ==========================================
col_json, col_action = st.columns([1, 1])

with col_json:
    with st.expander("📥 View Incoming Webhook Payload", expanded=False):
        st.json(features)

with col_action:
    run_engine = st.button("🚀 EXECUTE RISK PIPELINE", type="primary", use_container_width=True)

if run_engine:
    st.divider()
    
    # --- ANIMATED PROGRESS ---
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.markdown("##### 📡 Intercepting Order Webhook...")
    time.sleep(0.5)
    progress_bar.progress(25)
    
    status_text.markdown("##### 🧬 Extracting CRM Features & Vectors...")
    time.sleep(0.5)
    progress_bar.progress(50)
    
    # --- STAGE 1: LightGBM ---
    status_text.markdown("##### ⚡ STAGE 1: LightGBM Probability Scoring...")
    df = pd.DataFrame([features])
    for c in ['payment_method', 'pincode_tier', 'category']:
        df[c] = df[c].astype('category')
        
    model_features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    prob = float(bst.predict(df[model_features])[0])
    
    time.sleep(0.5)
    progress_bar.progress(75)
    
    # Display Stage 1 Results
    st.markdown("### 📊 Stage 1: Fast ML Filter")
    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted Fraud Risk", f"{prob*100:.1f}%")
    m2.metric("Operational Capacity Threshold", f"{threshold*100:.1f}%")
    m3.metric("Cost Budget Allocation", "Top 20%")
    
    if prob <= threshold:
        progress_bar.progress(100)
        status_text.empty()
        
        st.markdown("<div class='badge-allow'>✅ STAGE 1 DECISION: AUTO-APPROVE</div>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="reasoning-box">
            <strong>System Log:</strong> Risk probability ({prob*100:.1f}%) is well below the operational budget threshold ({threshold*100:.1f}%). 
            Order bypasses Stage 2 LLM and is cleared for immediate fulfillment.
        </div>
        """, unsafe_allow_html=True)
        
    else:
        status_text.markdown("##### 🧠 STAGE 2: Routing to LLM Triage Agent...")
        time.sleep(0.5)
        progress_bar.progress(90)
        
        st.markdown("<hr style='border: 1px dashed #334155'>", unsafe_allow_html=True)
        st.markdown("### 🤖 Stage 2: OpenAI Deep Triage")
        
        with st.spinner("Analyzing context..."):
            order_series = df.iloc[0]
            result = agent.triage_order(order_series)
            
            progress_bar.progress(100)
            status_text.empty()
            
            decision = result.get("decision", "ERROR")
            reasoning = result.get("reasoning", "Error connecting to OpenAI API.")
            
            if decision == "ALLOW":
                st.markdown("<div class='badge-allow'>✅ FINAL DECISION: OVERRIDE & ALLOW</div>", unsafe_allow_html=True)
            elif decision == "VERIFY_MANUALLY":
                st.markdown("<div class='badge-verify'>⚠️ FINAL DECISION: VERIFY MANUALLY</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-restrict'>🛑 FINAL DECISION: RESTRICT COD</div>", unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="reasoning-box">
                <strong>Agent Reasoning:</strong><br><br>
                {reasoning}
            </div>
            """, unsafe_allow_html=True)

