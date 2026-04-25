import os
import json
import requests

GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = "llama-3.3-70b-versatile"


def _headers() -> dict:
    if not GROQ_API_KEY:
        raise RuntimeError(
            "Groq API key not configured. Get a free key at https://console.groq.com "
            "and add GROQ_API_KEY to your .env file."
        )
    return {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }


def _call(messages: list, max_tokens: int = 700, temperature: float = 0.3) -> str:
    resp = requests.post(
        GROQ_URL,
        headers=_headers(),
        json={
            "model": MODEL,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": messages,
        },
        timeout=30,
    )
    if not resp.ok:
        try:
            detail = resp.json().get("error", {}).get("message", resp.text[:300])
        except Exception:
            detail = resp.text[:300]
        raise RuntimeError(f"Groq API {resp.status_code}: {detail}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def run(benchmark: dict, generic: dict, margin: dict, strategy: dict, my_price: float) -> dict:
    context = {
        "my_price": my_price,
        "price_benchmark": {
            "position": benchmark.get("position"),
            "market_avg": benchmark.get("market_avg"),
            "market_low": benchmark.get("market_low"),
            "market_high": benchmark.get("market_high"),
            "pct_diff_from_avg": benchmark.get("pct_diff"),
            "insight": benchmark.get("insight"),
        },
        "generic_substitution": {
            "opportunity": generic.get("opportunity"),
            "generic_name": generic.get("generic_name"),
            "generic_price": generic.get("generic_price"),
            "savings_pct": generic.get("savings_pct"),
            "insight": generic.get("insight"),
        },
        "margin_optimization": {
            "suggested_price": margin.get("suggested_price"),
            "current_margin_pct": margin.get("current_margin"),
            "optimal_margin_pct": margin.get("optimal_margin"),
            "target_margin_pct": margin.get("target_margin"),
            "margin_gap": margin.get("margin_gap"),
            "insight": margin.get("insight"),
        },
        "competitive_strategy": {
            "top_strategies": [s["name"] for s in strategy.get("top3", [])],
            "monthly_impact": strategy.get("monthly_impact"),
            "impact_label": strategy.get("impact_label"),
            "insight": strategy.get("insight"),
        },
    }

    prompt = f"""You are a pharmacy business intelligence AI. Based on the structured analysis below, generate a final pricing recommendation for a pharmacy owner.

AGENT ANALYSIS DATA:
{json.dumps(context, indent=2)}

Respond ONLY with a valid JSON object (no markdown, no explanation outside JSON) with exactly these fields:
{{
  "decision": "<one of: KEEP PRICE | REDUCE PRICE | RAISE PRICE | PROMOTE GENERIC | BUNDLE OFFER>",
  "confidence": <integer 50-98>,
  "rationale": "<2-3 sentence business reasoning for the decision, specific to the data above>",
  "suggested_price": <float, the optimal price to set>,
  "offer_strategy": "<short name of the best offer strategy, e.g. '90-Day Refill Bundle'>",
  "top3_actions": ["<action 1>", "<action 2>", "<action 3>"],
  "business_scenario": "<1-2 sentence plain-English explanation of what happens if the pharmacy follows this recommendation, with specific dollar figures>",
  "monthly_impact": <estimated monthly revenue/profit impact as a float>,
  "impact_label": "<human-readable impact, e.g. '+$240/mo'>"
}}"""

    raw = _call([{"role": "user", "content": prompt}])

    if raw.startswith("```"):
        raw = raw.split("```", 2)[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    result = json.loads(raw)

    required = ["decision", "confidence", "rationale", "suggested_price",
                "offer_strategy", "top3_actions", "business_scenario",
                "monthly_impact", "impact_label"]
    for k in required:
        if k not in result:
            raise ValueError(f"Missing key in AI response: {k}")

    result["ai_powered"] = True
    result["model"] = MODEL
    return result


def chat_followup(message: str, context: dict) -> str:
    system = f"""You are PharmaLens AI, a pharmacy pricing intelligence assistant.
You have already analyzed the following drug pricing data for a pharmacy owner:

{json.dumps(context, indent=2)}

Answer the pharmacist's follow-up question concisely and specifically. Reference the actual numbers from the analysis. Give actionable, direct advice. Keep response under 150 words."""

    return _call(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": message},
        ],
        max_tokens=350,
        temperature=0.4,
    )
