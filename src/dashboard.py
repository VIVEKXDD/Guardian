import streamlit as st
import pandas as pd
import lightgbm as lgb
import os
import time
from dotenv import load_dotenv
from stage2_llm import LLMTriageAgent
import json

# ==========================================
# PAGE CONFIGURATION & SESSION STATE
# ==========================================
st.set_page_config(
    page_title="Guardian Risk Engine",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize Session State for form presets
if "order_id" not in st.session_state:
    st.session_state.update({
        "order_id": "ORD_DEMO_004",
        "payment_method": "COD",
        "pincode_tier": "Tier_3",
        "category": "Footwear",
        "order_value": 2500,
        "discount": 0,
        "past_orders": 2,
        "past_returns": 1,
        "past_rtos": 0,
        "run_pipeline": False
    })

def set_preset(preset_name):
    if preset_name == "low_risk":
        st.session_state.update({
            "order_id": "ORD_0000516", "payment_method": "COD", "pincode_tier": "Tier_1", 
            "category": "Footwear", "order_value": 1500, "discount": 0, 
            "past_orders": 2, "past_returns": 0, "past_rtos": 0, "run_pipeline": True
        })
    elif preset_name == "high_risk":
        # Sample 15: 3/4 Returns, COD
        st.session_state.update({
            "order_id": "ORD_0004049", "payment_method": "COD", "pincode_tier": "Tier_3", 
            "category": "Footwear", "order_value": 4500, "discount": 0, 
            "past_orders": 4, "past_returns": 3, "past_rtos": 0, "run_pipeline": True
        })
    elif preset_name == "edge_case":
        # Sample 14: 100% RTO but only 1 order, COD
        st.session_state.update({
            "order_id": "ORD_0005721", "payment_method": "COD", "pincode_tier": "Tier_2", 
            "category": "Footwear", "order_value": 3000, "discount": 0, 
            "past_orders": 1, "past_returns": 0, "past_rtos": 1, "run_pipeline": True
        })

# ==========================================
# CUSTOM CSS FOR PREMIUM AESTHETICS
# ==========================================
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
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

    .stMetric {
        background-color: #1E293B;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #334155;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    
    .badge-allow {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #10B981;
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .badge-verify {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #F59E0B;
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 10px;
    }
    
    .badge-restrict {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
        padding: 10px 20px;
        border-radius: 8px;
        border: 1px solid #EF4444;
        font-weight: 600;
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 10px;
    }
    
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
    
    .empty-state {
        padding: 40px;
        text-align: center;
        border: 2px dashed #334155;
        border-radius: 12px;
        color: #94A3B8;
        margin-top: 20px;
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
    <p>Proactive Return & RTO Risk Scoring for Indian E-commerce</p>
</div>
""", unsafe_allow_html=True)

# ==========================================
# SIDEBAR (CONTROL PANEL)
# ==========================================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2083/2083213.png", width=60)
    st.markdown("### ⚡ Quick Presets (Video Ready)")
    st.markdown("Load pre-configured demo cases:")
    
    col_p1, col_p2, col_p3 = st.columns(3)
    col_p1.button("✅ Low Risk", on_click=set_preset, args=("low_risk",), use_container_width=True)
    col_p2.button("🛑 High Risk", on_click=set_preset, args=("high_risk",), use_container_width=True)
    col_p3.button("🤔 Edge Case", on_click=set_preset, args=("edge_case",), use_container_width=True)
    
    st.divider()
    
    st.markdown("#### 📦 Order Details")
    order_id = st.text_input("Order ID", key="order_id")
    
    pm_options = ["COD", "Prepaid"]
    pm_idx = pm_options.index(st.session_state.payment_method)
    payment_method = st.selectbox("Payment", pm_options, index=pm_idx, key="pm_select")
    st.session_state.payment_method = payment_method
    
    tier_options = ["Tier_1", "Tier_2", "Tier_3"]
    tier_idx = tier_options.index(st.session_state.pincode_tier)
    pincode_tier = st.selectbox("Tier", tier_options, index=tier_idx, key="tier_select")
    st.session_state.pincode_tier = pincode_tier
        
    cat_options = ["Fashion", "Footwear", "Electronics", "Home", "Beauty"]
    cat_idx = cat_options.index(st.session_state.category)
    category = st.selectbox("Category", cat_options, index=cat_idx, key="cat_select")
    st.session_state.category = category
    
    order_value = st.number_input("Value (₹)", min_value=100, max_value=50000, step=100, key="order_value")
    discount = st.slider("Discount Applied (%)", 0, 50, key="discount")
    
    st.divider()
    
    st.markdown("#### 👤 Historical CRM Data")
    past_orders = st.number_input("Total Past Orders", 0, 100, key="past_orders")
    col_ret, col_rto = st.columns(2)
    with col_ret:
        past_returns = st.number_input("Past Returns", 0, past_orders, key="past_returns")
    with col_rto:
        past_rtos = st.number_input("Past RTOs", 0, past_orders, key="past_rtos")

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
    run_btn = st.button("🚀 EXECUTE RISK PIPELINE", type="primary", use_container_width=True)
    if run_btn:
        st.session_state.run_pipeline = True

if not st.session_state.run_pipeline:
    st.markdown("""
    <div class="empty-state">
        <h3>Awaiting Order Input</h3>
        <p>Use the Quick Presets on the left to load a scenario, or click <strong>Execute Risk Pipeline</strong> to begin.</p>
    </div>
    """, unsafe_allow_html=True)
else:
    st.divider()
    
    # --- ANIMATED PROGRESS ---
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    status_text.markdown("##### 📡 Intercepting Order Webhook...")
    time.sleep(0.4)
    progress_bar.progress(25)
    
    status_text.markdown("##### 🧬 Extracting CRM Features & Vectors...")
    time.sleep(0.4)
    progress_bar.progress(50)
    
    # --- STAGE 1: LightGBM ---
    status_text.markdown("##### ⚡ STAGE 1: LightGBM Probability Scoring...")
    df = pd.DataFrame([features])
    for c in ['payment_method', 'pincode_tier', 'category']:
        df[c] = df[c].astype('category')
        
    model_features = ['payment_method', 'pincode_tier', 'category', 'order_value', 'discount_percent', 'past_order_count', 'past_return_count', 'past_rto_count', 'past_return_rate', 'past_rto_rate']
    prob = float(bst.predict(df[model_features])[0])
    
    time.sleep(0.4)
    progress_bar.progress(75)
    
    # Display Stage 1 Results
    st.markdown("### 📊 Stage 1: ML Risk Engine (Pre-Shipment)")
    m1, m2, m3 = st.columns(3)
    m1.metric("Predicted Fraud Risk", f"{prob*100:.1f}%")
    m1.caption("Probability of Return/RTO")
    
    m2.metric("Operational Capacity Threshold", f"{threshold*100:.1f}%")
    m2.caption("Score cutoff for the 20% review budget")
    
    m3.metric("Cost Budget Allocation", "Top 20%")
    m3.caption("Max daily volume we can manually verify")
    
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
        time.sleep(0.4)
        progress_bar.progress(90)
        
        st.markdown("<hr style='border: 1px dashed #334155'>", unsafe_allow_html=True)
        st.markdown("### 🤖 Stage 2: OpenAI Deep Reasoning")
        
        with st.spinner("Analyzing customer history vs. transaction risk..."):
            order_series = df.iloc[0]
            result = agent.triage_order(order_series)
            
            progress_bar.progress(100)
            status_text.empty()
            
            decision = result.get("decision", "ERROR")
            reasoning = result.get("reasoning", "Error connecting to OpenAI API.")
            
            if decision == "ALLOW":
                st.markdown("<div class='badge-allow'>✅ FINAL TIER: OVERRIDE & ALLOW</div>", unsafe_allow_html=True)
            elif decision == "VERIFY_MANUALLY":
                st.markdown("<div class='badge-verify'>⚠️ FINAL TIER: VERIFY MANUALLY</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='badge-restrict'>🛑 FINAL TIER: RESTRICT COD</div>", unsafe_allow_html=True)
                
            st.markdown(f"""
            <div class="reasoning-box">
                <strong>Agent Reasoning:</strong><br><br>
                {reasoning}
            </div>
            """, unsafe_allow_html=True)
            
    # Reset pipeline run state so they can use presets cleanly again
    st.session_state.run_pipeline = False

