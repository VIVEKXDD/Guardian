# 5-Minute Video Script: Guardian AI Risk Engine

> **Rubric Alignment Checklist:**
> - 🎯 **Problem Taste (0:00 - 0:20):** High-stakes Indian e-commerce unit economics (COD RTO + Returns). Proactive prevention, not reactive disputes.
> - 🛠️ **Build Quality & Live Demo (0:20 - 2:30):** Fully structured, runnable repo (FastAPI + LightGBM + Streamlit + OpenAI). Clean modularity and real-time execution.
> - 🧠 **AI Judgment (2:30 - 3:30):** The right tool in the right place—and where *not* to use one (LightGBM for 80% volume; LLM reserved strictly for top 20% ambiguous cases).
> - 🔧 **Failure Recovery (3:30 - 4:30):** What broke at 2 AM and how we fixed it (the 99% unconstrained flagging trap & the Sample 14 $n=1$ calibration bug).
> - 🔍 **Honest Limitations (4:30 - 5:00):** Synthetic data grounding and real-world deployment roadmap.

---

## 1. Problem Taste: Why This Matters (0:00 - 0:20)
*Visual: Speaking to camera. Crisp delivery, immediate hook.*

"In Indian e-commerce, Returns and Cash-on-Delivery RTO—Return to Origin—are silent margin killers. In fashion and footwear, return rates regularly cross 30%, and COD RTOs exceed 35% in tier-2 and tier-3 pincodes. When an order fails, the merchant absorbs both forward and reverse logistics. 

Most tools today are purely reactive—they help you gather video proof for disputes *after* the cash is gone. I built **Guardian**: a proactive, two-stage hybrid AI risk engine that intercepts and triages high-risk orders *before* the warehouse packs the box."

---

## 2. Build Quality & Live Demo (0:20 - 2:30)
*Visual: Screen recording of the Streamlit dashboard (`localhost:8501`). Clean, dark-mode UI.*

"Let's see it run. The repo is structured as an end-to-end pipeline: a FastAPI backend serving risk scores, an optimized LightGBM model, and this Streamlit operational dashboard designed for fraud review teams.

*(Click the 'Low Risk' preset)*
"Scenario one: A standard, low-risk customer. Clean order history, prepaid payment, tier-1 pincode. When I execute the pipeline, Stage 1—our LightGBM classifier—evaluates historical returns, order value, and pincode risk. It scores the fraud probability at roughly 30%. Because this is safely below our operational capacity threshold of 51.2%, it is instantly **Auto-Approved**. It runs in under 15 milliseconds with zero customer friction and zero LLM cost.

*(Click the 'High Risk' preset)*
"Scenario two: High fraud risk. The customer has returned 3 of their last 4 orders, has an RTO history, and is ordering high-value electronics via Cash-on-Delivery. 
"Watch what happens: Stage 1 scores this at over 65%, immediately breaching the 51.2% threshold and routing it to Stage 2. Stage 2 doesn't use hardcoded regex or brittle rules; it triggers an OpenAI reasoning agent. The agent examines the full customer profile and outputs **RESTRICT_COD**, accompanied by plain-English audit reasoning. The business avoids an almost certain ₹200 logistics loss.

*(Click the 'Edge Case' preset)*
"Now, look at Scenario three: The Edge Case. This is Order ORD_0005721. The customer has a 100% historical RTO rate. A primitive rule engine would instantly block or restrict this customer. 
"Stage 1 flags the risk. But look at Stage 2's reasoning: the AI recognizes that the customer only has **one past order** ($n=1$). A 100% rate on a single order is thin statistical evidence. Instead of blocking the sale and angering an honest customer, Guardian nuances the decision to **VERIFY_MANUALLY**, instructing the support desk to make a 30-second confirmation call. That's real, human-level triage."

---

## 3. AI Judgment: Right Tool in the Right Place (2:30 - 3:30)
*Visual: Switch to the Mermaid Architecture diagram in `ARCHITECTURE.md` or README.*

"A central architectural decision in Guardian is **where we chose NOT to use an LLM**.

If you pass 10,000 orders a day through a multi-modal or frontier LLM, your API bills will bankrupt you, and a 2-second p99 latency will break checkout conversion. 

So we applied AI judgment:
1. **LightGBM does the heavy lifting:** It processes tabular features—frequency encoding, historical return ratios, discount depth—in milliseconds. It filters out the bottom 80% of clean traffic at virtually zero marginal cost.
2. **The LLM is reserved strictly for the top 20% ambiguous tail:** We only spend LLM compute when multi-variable qualitative reasoning is genuinely required—like balancing small sample sizes, detecting compensating factors like prepaid payment, or explaining decisions to human review teams. Fast tabular ML where speed matters; deep generative reasoning where context matters."

---

## 4. Failure Recovery: What Broke at 2 AM (3:30 - 4:30)
*Visual: Highlight the Results & Metrics table in `README.md`.*

"The true measure of an engineering build is what broke and how you recovered. Two major issues broke during this project:

**First: The Unconstrained Optimization Trap.** 
When we first ran threshold optimization to minimize total business costs, the optimizer outputted a threshold of 0.01—it wanted to flag 99% of all orders. Why? Because the financial penalty of missed fraud (₹150–₹250) mathematically dwarfs a ₹10 review call. Unconstrained math broke operational reality. 
*How we recovered:* We redesigned the objective into a **capacity-constrained optimization**. We locked the manual review capacity to a realistic 20% of daily volume. At that exact 20% budget, our frozen LightGBM model captures **29.14% of all fraud**, validated via 1,000-resample bootstrap confidence intervals with zero data leakage.

**Second: The Sample Size Calibration Error.**
In our early Stage 2 prompt tests, the LLM actually failed that edge case I showed you. It saw '100% RTO' and over-weighted a thin sample of $n=1$, issuing a harsh restriction. 
*How we recovered:* Instead of hiding the failure, we treated prompt design like an engineering specification. We introduced explicit statistical calibration guidelines in the system prompt—instructing the model to evaluate sample sizes and downgrade confidence when $n < 3$. That fixed the error and produced calibrated, trustworthy triage."

---

## 5. Honest Limitations & Next Steps (4:30 - 5:00)
*Visual: Back to speaking to camera.*

"To be completely honest about limitations: because real Indian e-commerce COD and return datasets are proprietary, our dataset is synthetic—carefully calibrated to published industry benchmarks. While our architecture—FastAPI backend, LightGBM engine, and Streamlit frontend—mirrors how this runs in production, our precision and recall metrics reflect learning those simulated distributions.

The next step is deploying Guardian as a Shopify webhook app, collecting live merchant outcome data, and creating a continuous retraining flywheel. 

Thank you."
