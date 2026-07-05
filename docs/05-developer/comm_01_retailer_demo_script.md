---
Document ID: "DEV-012"
Title: "COMM-01 — PSV Retailer Demo Script (10 Minutes)"
Owner: "Development Team"
Audience: "Developer"
Module: "PSV"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# COMM-01 — PSV Retailer Demo Script (10 Minutes)
**Sprint**: PSV-COMM-001 Wave 1
**Audience**: Retailer / Brand Owner (decision maker, non-technical)
**Format**: Live product demo using SMRITI Presentation Suite → PSV deck
**Duration**: 10 minutes hard cap
**Goal**: Retailer says "I want to run a pilot"

---

## Pre-Demo Checklist

```
Before entering the meeting:
  [ ] smriti-presentation.html loaded at PSV deck (Inventory Visibility)
  [ ] Internet connection confirmed (or offline fallback ready)
  [ ] One-pager printed or on second screen: psv_executive_one_pager.md
  [ ] Know the retailer's approximate distributor count
  [ ] Know their primary product category (footwear / apparel / FMCG)
```

---

## The 10-Minute Script

### 00:00 — 00:45 | Hook (The Problem)

**What you say:**

> "Ek simple sawaal — aapke distributor ke paas abhi kitna stock hai?
> Exact number."

*(Pause. Let them answer. Most will say "approximate pata hai" or "next visit pe dekhenge".)*

> "Yahi problem hai. Aap ne stock bheja, invoice cut hui — aur wahan se
> aapki visibility khatam ho gayi. PSV wahi karta hai jo aap abhi nahi kar sakte:
> real-time mein dekhna ki aapka maal kahan hai, kitna bikaa, aur kitna ruk gaya."

**Slide to show**: Slide 1 — *"The Distribution Visibility Gap"*

---

### 00:45 — 02:30 | The Three Numbers (Core Value)

**What you say:**

> "PSV teen numbers track karta hai. Teen hi kaafi hain."

**Number 1 — Sell-Through %**
> "Aapne 1,000 pcs bheje. Distributor ne 850 bech diye.
> Sell-Through = 85%. Aapko pata chal gaya — yeh distributor fast hai."

**Number 2 — Weeks of Cover (WOC)**
> "Ek doosra distributor hai. Uske paas 140 pcs hain, 35 pcs/week bikta hai.
> WOC = 4 weeks. Matlab 4 hafte mein stockout ho jaayega.
> PSV aapko 4 hafte pehle alert karta hai — reorder ke liye time milta hai."

**Number 3 — Dead Stock Value**
> "Teen mahine se kuch nahi bika? Woh capital lock hai.
> PSV usse surface karta hai before it becomes a write-off."

**Slide to show**: Slide 2 — *"Distributor Sell-Through Tracker"* (run the simulation — click "Log 50 Secondary Sales")

---

### 02:30 — 04:30 | Live Demo (The Proof)

**What you do**: Run the interactive sell-through simulator.

> "Dekho — main secondary sales simulate kar raha hoon.
> Jaise jaise distributor ke outlets pe bikri hoti hai,
> Sell-Through rate update hota hai, WOC recalculate hota hai,
> aur agar koi location pe stockout risk hai — alert aa jaata hai."

**Slide to show**: Slide 3 — *"Reorder & Replenishment Intelligence"*

> "Aur yeh seedha ek recommended action mein convert ho jaata hai.
> PSV suggest karta hai — kahan se kahan transfer karo.
> Aap decide karte ho. System recommend karta hai."

*(Click the transfer simulation on Slide 8 — "Network Stock Transfer Simulator")*

---

### 04:30 — 06:00 | The ROI Story

**What you say:**

> "50,000 item network mein agar sirf 6% stockouts prevent ho jayein —
> woh 3,000 bestsellers hain jo consumer tak pahunch gaye.
> ₹500 average margin per item — woh ₹15 Lakh annual margin recovery hai."

*(Show the one-pager ROI table if printed.)*

> "Yeh conservative estimate hai. Aapke product category ke hisaab se
> adjust ho sakta hai. Lekin direction clear hai — PSV pays for itself."

---

### 06:00 — 07:30 | How It Works (30 seconds, non-technical)

**What you say:**

> "Isko implement karne ke liye aapke distributor ka system change nahi karna.
> Woh Excel mein bhi data upload kar sakta hai.
> SMRITI usse process karta hai — aapko dashboard milta hai.
> Aapke ERPNext ya existing billing system ko touch nahi karta."

**Key message**: *Non-invasive. Distributor-friendly. Brand-owned visibility.*

---

### 07:30 — 09:00 | Proof Point (Tattly Threads Reference)

**What you say:**

> "Hum abhi ek footwear brand ke saath pilot kar rahe hain.
> Unka Phase 1 complete hai — data upload, ledger, reconciliation, exception alerts.
> Woh pehla live distributor upload karne wale hain."

*(Do not over-promise. Do not quote specific results yet — pilot is ongoing.)*

---

### 09:00 — 10:00 | The Ask

**What you say:**

> "Hum 30-day pilot offer kar rahe hain — ek distributor, ek brand.
> Aap dekhoge ki yeh aapke actual data pe kaise kaam karta hai.
> Success criteria hum milke define karenge — WOC accuracy, sell-through tracking,
> aur exception alert response time."

> "Kya aap apne ek distributor ke saath start karna chahenge?"

---

## Likely Questions After Demo

| Question | Response |
|----------|----------|
| "Distributor cooperate karega?" | "Excel upload se shuru hota hai. Unhe kuch install nahi karna." |
| "ERPNext zaroori hai?" | "Nahi. PSV standalone kaam karta hai." |
| "Data secure hai?" | "SMRITI aapke server pe run karta hai. Data aapke paas rehta hai." |
| "Kitna time lagega setup mein?" | "Pilot onboarding: 3-5 din. Ek distributor ke liye." |
| "Cost kya hai?" | "Pilot ke liye structure hai — milte hain [COMM-04 output needed here]" |

> [!IMPORTANT]
> **COMM-04 dependency**: Cost question → refer to Pilot Offer Structure.
> Do not answer pricing without the COMM-04 document. Say "structure share karta hoon."

---

## Demo Failure Recovery

| Problem | Recovery |
|---------|---------|
| Internet fails | "Offline mode hai — same demo, cached data" |
| Slide loads slowly | Go to one-pager — walk through the 3 numbers verbally |
| Retailer disengages | "Ek number batao — aapke best distributor ka Sell-Through kya hoga?" |
| "Yeh sab already Excel mein karta hoon" | "Excel mein WOC automatically recalculate hota hai jab secondary sales aati hai?" |

---

## Demo Done — What Next

```
If interest shown:
  → Share one-pager (psv_executive_one_pager.md)
  → Schedule pilot structure conversation (COMM-04 output)
  → Ask: "Konsa distributor sabse zyada stock rakhta hai?"

If not convinced:
  → "Koi problem nahi. Ek specific problem share kijiye —
     dead stock, stockout, ya sell-through tracking —
     hum specifically wahan demo karein?"
```


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL