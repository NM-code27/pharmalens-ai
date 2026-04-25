# ⚗️ PharmaLens AI — Pharmacy Pricing Intelligence Platform

A full-stack business intelligence dashboard that helps pharmacy owners price competitively, detect margin gaps, and design optimal discount strategies using RxNav-powered drug intelligence.

---

## 🎯 Business Problem

Small pharmacies sell the same medicines as large chains (CVS, Walgreens, Walmart) without knowing:
- What competitors are charging
- Whether they are overpriced or underpriced
- What generic alternatives could save their customers money
- What pricing strategy maximizes both volume and margin

**PharmaLens AI solves this with 4 specialized AI agents and a real drug intelligence layer.**

---

## 💡 Why RxNav?

[RxNav](https://rxnav.nlm.nih.gov/) is a free, no-key-required API from the U.S. National Library of Medicine (NLM). It provides:
- Drug name normalization (brand → generic)
- RxCUI identifiers for drug classification
- Brand and generic drug relationships

This ensures PharmaLens AI always uses real, verified drug data rather than guessing.

---

## 📊 Why Are Prices Simulated?

Real pharmacy prices are not publicly available via free API. Scraping is legally risky and unreliable.

PharmaLens AI uses **deterministic price simulation** — prices are computed from a hash of the drug name, so:
- Same drug = same competitor prices every time
- No randomness or refresh surprises
- Realistic spread: CVS/Walgreens price at premium, Costco/Online at discount
- Transparent and clearly disclosed in the UI

---

## 🤖 AI Agents

| Agent | Role |
|-------|------|
| **Price Benchmark Agent** | Compares user price vs market avg/low/high |
| **Generic Substitution Agent** | Estimates savings from brand → generic switch |
| **Margin Optimization Agent** | Suggests optimal price for target margin |
| **Competitive Strategy Agent** | Recommends offer/bundle strategy |
| **Orchestrator** | Combines all agents → final KEEP/REDUCE/RAISE/PROMOTE/BUNDLE decision |

---

## 🚀 How to Run

```bash
# 1. Clone / unzip the project
cd pharmalens_ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Copy env file (optional)
cp .env.example .env

# 4. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

---

## 💊 Demo Drugs to Try

| Drug | Type | Est. Price |
|------|------|-----------|
| Lipitor | Brand (statin) | $22.50 |
| Metformin | Generic (diabetes) | $5.50 |
| Ibuprofen | OTC analgesic | $4.00 |
| Amoxicillin | Antibiotic | $12.00 |
| Omeprazole | Acid reducer | $11.00 |
| Levothyroxine | Thyroid | $13.00 |

---

## 📁 Project Structure

```
pharmalens_ai/
├── app.py                     # Flask routes
├── requirements.txt
├── README.md
├── .env.example
├── services/
│   ├── rxnav_service.py       # RxNav API integration
│   └── pricing_engine.py      # Deterministic competitor pricing
├── agents/
│   ├── price_benchmark_agent.py
│   ├── generic_substitution_agent.py
│   ├── margin_optimization_agent.py
│   ├── competitive_strategy_agent.py
│   └── orchestrator.py
├── templates/
│   └── index.html             # SaaS dashboard
└── static/
    ├── css/style.css
    └── js/app.js
```

---

## ⚙️ Tech Stack

- **Backend**: Flask, Python, requests, python-dotenv
- **Drug Data**: RxNav NLM API (free, no key)
- **Frontend**: HTML, CSS, JavaScript, Chart.js
- **Design**: Glassmorphism, dark theme, Syne + DM Mono fonts

---

*PharmaLens AI — Built for pharmacy owners who compete on intelligence, not just price.*
