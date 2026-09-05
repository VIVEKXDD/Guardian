# Video Script: Guardian AI Risk Engine (5 Minutes)

## 1. The Problem (0:00 - 0:20)
*Visual: Speaking to camera, perhaps showing a quick headline on screen about Indian e-commerce losses.*
"In Indian e-commerce, Returns and RTOs—Return to Origin—are a massive cost center. Fashion return rates regularly hit 30%, and Cash-on-Delivery RTO rates can exceed 40% in certain pincodes. The problem is that current fraud tools are reactive; they help you dispute a return *after* you've lost the money. I built **Guardian**, a two-stage hybrid AI risk engine, to proactively score and triage that risk *before* the order even ships."

## 2. Live Demo (0:20 - 2:30)
*Visual: Screen recording of the Streamlit Dashboard. Clean, dark-mode UI is visible.*
"Let's look at it in action. I've built this interactive dashboard to simulate what the backend API does in real-time when a webhook drops an order into the system.

*(Click the 'Low Risk' preset)*
"First, a standard low-risk order. The customer has a clean history. I execute the pipeline. Stage 1, our LightGBM model, instantly scores the fraud risk at around 30%. Because this is below our operational threshold, it's auto-approved. Zero friction for the good customer.

*(Click the 'High Risk' preset)*
"Now, let's look at a high-risk scenario. This customer has returned 3 out of their 4 past orders, and they're attempting another high-value COD purchase. I hit execute. 
"Stage 1 immediately flags the risk at over 60%, pushing it into Stage 2. Stage 2 isn't a hard-coded rule; it's an OpenAI-powered LLM agent. It reads the customer context and makes a judgment. Here, it restricts COD and explains exactly why in the system log, preventing the shipping loss.

*(Click the 'Edge Case' preset)*
"But here is where the hybrid approach shines: the Edge Case. This customer has a 100% RTO rate. A simple rule-based system would ban them instantly. Let's see what Guardian does. 
"Stage 1 flags it, but the LLM in Stage 2 notices something: the sample size is only 1. A 100% RTO rate on a single past order is thin evidence. Instead of blocking the sale, the LLM nuances the decision to `VERIFY_MANUALLY`, asking customer support to simply call the buyer. The AI recognizes context."

## 3. Architecture + Why AI (2:30 - 3:30)
*Visual: Bring up the Mermaid Architecture diagram on screen.*
"Why use this two-stage architecture instead of just one big model?
"First, cost and speed. You can't run a 2-second LLM call on 10,000 orders a day—it's too slow and too expensive. Stage 1 is a heavily optimized LightGBM model. It acts as a fast, cheap filter, Auto-Approving the bottom 80% of safe traffic in milliseconds. 
"We only route the highly suspicious top 20% to the Stage 2 LLM. We need the LLM because risk isn't binary. The LLM can reason about complex edge cases—like noticing that a Prepaid payment method mitigates the risk of a past RTO—much better than a fragile tree of `if/else` statements."

## 4. Metrics, Cost Table & Failure Case (3:30 - 4:30)
*Visual: Show the README Metrics and Cost Table section.*
"To prove this works, I evaluated Guardian using a strict, leakage-free methodology. 
"Instead of an unconstrained model that tries to flag everything to save money, I built a capacity-constrained optimizer. We assumed a real-world scenario where the manual review team can only handle calling the top 20% of orders. At that specific 20% budget cutoff, Stage 1 successfully intercepts **29.14%** of all total fraud. We are maximizing the ROI of the human review team without needing to hire more people.

"And for transparency, I documented the AI's failures. Early on, the Stage 2 LLM actually *failed* that edge case I just showed you. It hallucinated that a 100% RTO rate on `n=1` orders was a massive threat. I had to explicitly calibrate the prompt to teach it statistical sample sizes, which restored human-level nuance to the agent."

## 5. Honest Limitations & Next Steps (4:30 - 5:00)
*Visual: Back to speaking to camera.*
"To be completely transparent, the biggest limitation of Guardian right now is the dataset. Because real COD and pincode-level RTO data is highly proprietary in India, I had to generate a synthetic dataset probabilistically calibrated to published industry reports. While the pipeline architecture is 100% production-ready—complete with a FastAPI backend and this Streamlit UI—the exact precision/recall numbers are tied to simulated data. 
"The next step would be deploying this alongside a real Shopify backend and fine-tuning the Stage 1 model on actual live traffic. 
"Thanks for watching."
