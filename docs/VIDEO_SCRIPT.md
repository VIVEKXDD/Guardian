# 5-Minute Video Script: Guardian AI Risk Engine (Final Refined)

> **Rubric Alignment Checklist:**
> - 🎯 **Problem Taste (0:00 - 0:20):** High-stakes Indian e-commerce unit economics (COD RTO + Returns). Proactive prevention, not reactive disputes. Contextualized against Razorpay's gap.
> - 🛠️ **Build Quality & Live Demo (0:20 - 2:30):** Fully structured, runnable repo (FastAPI + LightGBM + Streamlit + OpenAI). Real-time execution across 3 live presets. Rigorous dataset justification (ASOS / Kaggle gaps).
> - 🧠 **AI Judgment (2:30 - 3:30):** The right tool in the right place — and where *not* to use one (LightGBM for 80% volume at sub-millisecond latency; LLM reserved for top 20% ambiguous cases).
> - 🔧 **Failure Recovery (3:30 - 4:30):** What broke and how it got fixed — the unconstrained-flagging trap and the Sample 14 ($n=1$) calibration bug.
> - 🔍 **Honest Limitations (4:30 - 5:00):** Synthetic data grounding, illustrative cost assumptions, real-world Shopify roadmap.

---

## 1. Problem Taste: Why This Matters (0:00 - 0:20)
*Visual: Speaking to camera. Crisp delivery, immediate hook.*

"In Indian e-commerce, returns and Cash-on-Delivery RTOs are silent margin killers. In fashion and footwear, return rates regularly cross 30%. COD RTOs exceed 35% in tier-2 and tier-3 pincodes. Every time an order fails, the merchant eats both the forward *and* the reverse shipping cost.

Here's the problem: the tools that exist today — proof-of-packing videos, dispute evidence platforms — only help you win the argument *after* the loss already happened. And Razorpay's own risk stack is strong on card fraud and chargebacks — but returns and RTO sit in a genuine gap outside that. Nobody's scoring the risk *before* the box ships. So I built **Guardian** — a two-stage hybrid AI risk engine that does exactly that."

---

## 2. Build Quality & Live Demo (0:20 - 2:30)
*Visual: Screen recording of the Streamlit dashboard (`localhost:8501`). Clean, dark-mode UI.*

"Let's see it work. Under the hood: a FastAPI backend serving risk scores, an optimized LightGBM model, and this dashboard, built for a fraud review team to actually use.

Before writing any model code, I went looking for real data. There's an academic return-prediction dataset from ASOS — but it's UK retail, no COD, no pincode signal, the two things that actually drive Indian RTO. Kaggle's Indian datasets are real too, but they're built for card fraud, a different problem entirely. So I built a probabilistic synthetic generator instead, calibrated to published Indian return and RTO rates — then spent real time hunting down near-deterministic shortcuts and one silently underfit model before trusting a single number that's about to show up on this screen.

*(Click the 'Low Risk' preset)*
"Scenario one. Clean order history, prepaid, tier-1 pincode. I hit execute — Stage 1 reads the return history, order value, and pincode risk, and scores this at around 30%. That's comfortably under our 51.2% operational threshold, so it's **Auto-Approved** instantly in single-digit milliseconds. Zero friction for a good customer, zero LLM spend.

*(Click the 'High Risk' preset)*
"Scenario two. This customer has returned 3 of their last 4 orders, has an RTO on record, and is placing a high-value electronics order — on COD. Watch: Stage 1 pushes this well past our threshold, straight into Stage 2. And Stage 2 isn't a wall of if/else rules — it's an OpenAI reasoning agent reading the full customer profile. It comes back with **RESTRICT_COD**, and it tells you exactly why. That's a business potentially saving an estimated ₹150–₹250 in logistics losses on one order.

*(Click the 'Edge Case' preset)*
"Now — this is the one I actually want you to pay attention to. Order ORD_0005721. This customer has a 100% historical RTO rate. A blunt rule engine bans this person on the spot, no questions asked.

Watch what Guardian does instead. Stage 1 flags it, sure. But Stage 2 catches something the rule can't: this customer has exactly **one** past order. A 100% rate on a sample of one isn't a pattern — it's a coin flip. So instead of blocking a possibly-honest customer, Guardian downgrades this to **VERIFY_MANUALLY** — a 30-second confirmation call instead of a lost sale. That's the difference between a rule and a judgment."

---

## 3. AI Judgment: The Right Tool in the Right Place (2:30 - 3:30)
*Visual: Switch to the architecture diagram (`ARCHITECTURE.md`).*

"One of the decisions I'm proudest of in this build is where we chose *not* to use an LLM.

Run 10,000 orders a day through a frontier model and two things happen: your API bill explodes, and your checkout latency tanks conversion. So we split the work by what each tool is actually good at.

LightGBM handles the volume — return ratios, discount depth, pincode history — in single-digit milliseconds, filtering the safe majority of traffic at close to zero cost. The LLM only gets called on the ambiguous top slice, where the decision genuinely needs judgment: weighing a thin sample size, noticing that a prepaid payment offsets a past RTO, explaining a decision in plain language a human reviewer can trust. Fast, cheap ML where speed matters. Real reasoning where context matters."

---

## 4. Failure Recovery: What Broke, and What We Learned (3:30 - 4:30)
*Visual: Highlight the Results & Metrics table in `README.md`.*

"The real test of a build isn't whether everything worked — it's what broke, and whether you caught it.

**First break: the unconstrained optimization trap.** When we first optimized purely for cost, the model told us to flag *99.95% of all orders* — because missing a fraud case costs so much more than one review call, the raw math says review everyone. That's not a working filter, that's Stage 1 doing nothing. So we reframed it: assume your review team can only realistically handle the top 20% of daily volume, and optimize *within* that constraint. At that 20% budget, Guardian catches **29.14% of all fraud** — a real, meaningful lift we confirmed isn't just noise, using a 1,000-resample bootstrap on the model's underlying ranking power.

**Second break: the sample-size blind spot.** Early on, Stage 2 saw '100% RTO rate' on a single order and slammed the door — restricted the customer outright. It wasn't wrong about the fact, it was wrong about the *weight* it gave a sample size of one. So we didn't patch around it — we rewrote the system prompt to explicitly reason about sample size before committing to a hard decision. That's the fix you just watched work in the edge-case demo."

---

## 5. Honest Limitations & Next Steps (4:30 - 5:00)
*Visual: Back to speaking to camera.*

"As I mentioned, this runs on carefully calibrated synthetic data, not a live merchant feed — so today's precision and recall numbers tell you the model learned the patterns I built in, not a guarantee of real-world performance yet. The architecture — FastAPI, LightGBM, Streamlit — is built to mirror production.

The real next step is plugging into an actual Shopify webhook, collecting real outcomes, and retraining on the real thing instead of my best-informed guess at it.

Returns don't have to stay silent. Thanks for watching."
