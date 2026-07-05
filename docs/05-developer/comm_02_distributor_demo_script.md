---
Document ID: "DEV-013"
Title: "COMM-02 — PSV Distributor Demo Script (15 Minutes)"
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

# COMM-02 — PSV Distributor Demo Script (15 Minutes)
**Sprint**: PSV-COMM-001 Wave 2
**Audience**: Distributor / Channel Partner (operational, field-level decision maker)
**Format**: Live product demo — PSV deck + exception flows
**Duration**: 15 minutes (distributor conversations take longer — more operational depth)
**Goal**: Distributor agrees to be the pilot partner

---

## Why Distributor Demos Are Harder

Distributors have different concerns than retailers:

| Retailer asks | Distributor asks |
|--------------|-----------------|
| "Kitna paisa bachega?" | "Mujhe extra kaam karna padega?" |
| "Meri visibility badhegi?" | "Mera data kahan jayega?" |
| "ROI kya hai?" | "Mera existing system change hoga?" |

**Core fear**: PSV feels like surveillance. Distributor thinks: "Brand mere paas nazar rakhne laga."

**Core message you must establish in first 2 minutes**:
> "PSV aapke liye bhi kaam karta hai, sirf brand ke liye nahi."

---

## Pre-Demo Checklist

```
Before entering the meeting:
  [ ] Know distributor's approximate SKU count and location count
  [ ] Know how they currently report stock to brand (Excel / WhatsApp / nothing)
  [ ] smriti-presentation.html loaded at PSV deck
  [ ] COMM-03 exception scenarios ready as backup stories
  [ ] COMM-08 success criteria document available (for closing)
```

---

## The 15-Minute Script

### 00:00 — 01:30 | Establish Trust First

**What you say:**

> "Main directly bolta hoon — yeh tool brand ke liye nahi banaya gaya.
> Yeh aapke liye bhi kaam karta hai.
>
> Aapke paas abhi ek problem hai — brand kabhi kabhi demand forecast galat karta hai
> aur aap over-stocked ho jaate ho. Ya under-stocked. Dono situations mein
> aap capital lose karte ho.
>
> PSV aapko wahi information deta hai jo aap brand ko dene mein hesitate karte ho —
> kyunki ab woh information aapke liye bhi useful hai."

*(Let this land. Don't rush to the demo.)*

---

### 01:30 — 03:30 | Their Problem, Their Language

**What you say:**

> "Ek sawaal — aapके godown mein abhi kaun se item 3 mahine se nahi bik rahe?"

*(Pause. Most will either say "pata nahi" or name something.)*

> "Aur woh kitne capital ka stock hai?"

*(Another pause. They rarely know the exact number.)*

> "PSV yeh number automatically nikalta hai.
> Aur phir woh suggest karta hai — yeh item kahan transfer karo,
> taaki fresh order lena na pade."

---

### 03:30 — 06:00 | Show the Dead Stock Scenario (COMM-03 Scenario 2)

**Slide to show**: Inventory Freshness & Aging

**What you say:**

> "Dekho — yeh aging chart hai. 0-30 din — active. 31-60 — slow.
> 61-90 — aging. 90 plus — dead stock.
>
> Aapke godown mein agar koi item 90+ din se hai —
> PSV usko surface karta hai. Value calculate karta hai.
> Aur ek suggestion deta hai — transfer karo, campaign lagao, ya brand ko return bhejo."

> "Yeh information aapki hai. Brand ko sirf summary jaati hai.
> Koi item-level surveillance nahi."

---

### 06:00 — 08:30 | Show the WOC Scenario (COMM-03 Scenario 1)

**Slide to show**: Distributor Sell-Through Tracker

**What you say:**

> "Doosri cheez — aapke paas ek size ki shortage hone wali hai.
> WOC — Weeks of Cover — batata hai kitne hafte ka stock bacha hai.
>
> Agar WOC 1.8 hai — matlab paanch mahine mein nahi, 12 din mein stockout hoga.
> PSV yeh 4 hafte pehle bata deta hai.
>
> Aap brand ko reorder request bhej sakte ho before outlets complain karne lagte hain.
> Aur brand bhi khush — kyunki aapne proactively data share kiya."

*(Run the sell-through simulation — click "Log 50 Secondary Sales")*

> "Har baar secondary sales aati hai — WOC update hota hai. Real-time."

---

### 08:30 — 10:30 | Show the Network Balancing (COMM-03 Scenario 3)

**Slide to show**: Network Stock Transfer Simulator

**What you say:**

> "Teesri situation — aapke Mumbai godown mein size 32 ka 120 pcs extra hai.
> Pune mein same size stockout chal raha hai.
>
> PSV yeh detect karta hai aur suggest karta hai:
> Mumbai se Pune ko transfer karo.
>
> Fresh purchase nahi, existing stock move hota hai.
> Brand ka fresh order nahi, aapka capital deploy nahi.
> Dono faida mein."

*(Click the "Balance Network Stock" button on the simulator)*

---

### 10:30 — 12:00 | Address the Real Fear

**What you say:**

> "Main jaanta hoon ek sawaal hai aapke mann mein —
> 'Brand ab mera poora data dekhega?'
>
> Sach yeh hai — brand ko Sell-Through % dikhta hai, item-level detail nahi.
> Aapke pricing margins, customer details, ya local adjustments —
> kuch nahi jaata.
>
> Aur honestly — agar brand ka data aapke liye bhi useful hai,
> toh yeh partnership hai, surveillance nahi."

---

### 12:00 — 13:30 | The Distributor Benefit Case

**What you say:**

> "Mere hisaab se PSV aapko teen cheezein deta hai:
>
> Ek — dead stock identify hone se pehle action le sakte ho.
> Do — brand ke saath conversation mein numbers hote hain, assumptions nahi.
> Teen — reorder timing improve hota hai — na over-stocked, na under-stocked."

---

### 13:30 — 15:00 | The Ask

**What you say:**

> "Hum ek 30-day pilot kar rahe hain — ek distributor, ek brand.
> Aapka kaam? Ek Excel template fill karna — weekly stock aur sales summary.
> 20 minute per week.
>
> 30 din baad hum milte hain aur dekhte hain kya nikla.
> Agar useful nahi laga — koi commitment nahi.
> Agar useful laga — phir aage baat karte hain."

---

## Distributor-Specific Objections

| Objection | Response |
|-----------|---------|
| "Mujhe kuch install karna padega?" | "Nahi. Sirf Excel template. WhatsApp pe bhi bhej sakte ho." |
| "Mera data secure hai?" | "Data brand ke server pe nahi — SMRITI ke secured instance pe." |
| "Brand meri pricing dekhega?" | "Nahi. Sirf sell-through % aur stock levels — koi pricing data nahi." |
| "Bahut kaam badh jayega" | "20 minute per week. Pehle hafte hum saath karenge." |
| "Pehle se Excel mein karta hoon" | "Same Excel — hum processor hain. Aap format same rakhte ho." |
| "Brand pressure ke liye use hoga?" | "PSV recommendation deta hai. Action aap lete ho. Force nahi." |

---

## Distributor Demo — Done. What Next

```
If interested:
  → Share COMM-08 success criteria
  → Confirm: pilot brand, pilot duration, data format
  → Schedule Week 1 onboarding (30 min)
  → Get one contact person for data coordination

If hesitant:
  → "Ek cheez batao — abhi brand se stock conversation kaise hoti hai?
     Hum wahi ek cheez improve karte hain pehle."

If declined:
  → Understand exact reason — data concern / effort concern / trust concern
  → Document for COMM-06 objection handling refinement
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