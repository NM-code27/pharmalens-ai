# ⚗️ PharmaLens AI — Pharmacy Pricing Intelligence Platform

A full-stack business intelligence dashboard that helps pharmacy owners price competitively, detect margin gaps, and design optimal discount strategies using RxNav-powered drug intelligence and Groq LLaMA 3.3 AI.

**Live Demo:** [Frontend on Vercel](https://pharmalens-ai.vercel.app) · **API:** [Backend on Render](https://pharmalens-ai.onrender.com)

---

## 🎯 Business Problem

Small pharmacies sell the same medicines as large chains (CVS, Walgreens, Walmart) without knowing:
- What competitors are charging
- Whether they are overpriced or underpriced
- What generic alternatives could save their customers money
- What pricing strategy maximizes both volume and margin

**PharmaLens AI solves this with 4 specialized AI agents powered by Groq LLaMA 3.3 and a real drug intelligence layer.**

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
| **Groq Orchestrator** | Combines all agents → final KEEP/REDUCE/RAISE/PROMOTE/BUNDLE decision via LLaMA 3.3 70B |

All AI inference runs on **Groq** using `llama-3.3-70b-versatile` — no fallbacks, no mock data.

---

## 🏗️ Architecture

```
Browser (Vercel)
    │
    ├── GET /              → index.html (static)
    ├── GET /static/*      → CSS / JS (static)
    └── POST /api/*        → Vercel rewrite proxy
                                │
                                ▼
                     Render (Flask + Gunicorn)
                                │
                     ┌──────────┴──────────┐
                     ▼                     ▼
               RxNav NLM API          Groq API
               (drug data)        (LLaMA 3.3 70B)
```

- **Frontend** — Pure static HTML/CSS/JS on Vercel. Uses relative `/api/` URLs.
- **Backend** — Flask on Render. All AI and drug data calls happen server-side.
- **Proxy** — `vercel.json` rewrites `/api/*` to Render — zero CORS issues.

---

## 🚀 Local Development

```bash
# 1. Clone the repo
git clone https://github.com/NM-code27/pharmalens-ai.git
cd pharmalens-ai

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
cp .env.example .env
# Edit .env and add your GROQ_API_KEY

# 4. Run the app
python app.py
```

Open **http://localhost:5000** in your browser.

---

## ☁️ Deployment

### Backend — Render (free)
1. Connect repo on [render.com](https://render.com)
2. Runtime: **Python 3**, Start Command: `gunicorn app:app`
3. Set env var: `GROQ_API_KEY=your_key_here`

### Frontend — Vercel (free)
1. Import repo on [vercel.com/new](https://vercel.com/new)
2. Framework: **Other**, Build Command: *(empty)*, Output: *(empty)*
3. No env vars needed — API key lives on Render only
4. Deploy — `vercel.json` handles the `/api/*` proxy automatically

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
├── app.py                          # Flask routes + /api/chat endpoint
├── index.html                      # Static root for Vercel
├── vercel.json                     # Vercel proxy config → Render
├── Procfile                        # gunicorn for Render
├── requirements.txt
├── README.md
├── .env.example
├── services/
│   ├── rxnav_service.py            # RxNav NLM API integration
│   └── pricing_engine.py           # Deterministic competitor pricing
├── agents/
│   ├── price_benchmark_agent.py
│   ├── generic_substitution_agent.py
│   ├── margin_optimization_agent.py
│   ├── competitive_strategy_agent.py
│   └── orchestrator.py             # Groq LLaMA 3.3 orchestration + chat
├── templates/
│   └── index.html                  # Flask template (local dev)
└── static/
    ├── css/style.css               # Dark glassmorphism UI
    └── js/app.js                   # Async chatbot + chart rendering
```

---

## ⚙️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Python, Gunicorn |
| AI | Groq API · LLaMA 3.3 70B Versatile |
| Drug Data | RxNav NLM API (free, no key required) |
| Frontend | HTML5, CSS3, Vanilla JS, Chart.js 4 |
| Fonts | Syne, DM Mono, Inter (Google Fonts) |
| Design | Dark glassmorphism, CSS custom properties |
| Deploy | Render (backend) + Vercel (frontend) |

---

*PharmaLens AI — Built for pharmacy owners who compete on intelligence, not just price.*
