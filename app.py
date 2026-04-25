from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os

load_dotenv()

from services.rxnav_service import get_drug_info
from services.pricing_engine import generate_competitor_prices, _estimate_base
from agents import price_benchmark_agent, generic_substitution_agent
from agents import margin_optimization_agent, competitive_strategy_agent, orchestrator

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/health")
def health():
    return jsonify({"status": "ok", "service": "PharmaLens AI"})


@app.route("/api/analyze-pricing", methods=["POST"])
def analyze_pricing():
    body = request.get_json(force=True)
    drug_name = (body.get("drug") or "").strip()
    if not drug_name:
        return jsonify({"error": "Drug name is required."}), 400

    my_price_raw = body.get("my_price")
    target_margin = float(body.get("target_margin") or 25)

    drug_info = get_drug_info(drug_name)

    if my_price_raw is not None and float(my_price_raw) > 0:
        my_price = float(my_price_raw)
    else:
        my_price = _estimate_base(drug_name)
        drug_info["price_estimated"] = True

    competitors = generate_competitor_prices(drug_name, my_price)

    benchmark = price_benchmark_agent.run(drug_info, my_price, competitors)
    generic   = generic_substitution_agent.run(drug_info, my_price, competitors)
    margin    = margin_optimization_agent.run(drug_info, my_price, target_margin, competitors)
    strategy  = competitive_strategy_agent.run(drug_info, my_price, benchmark, generic, margin)

    try:
        final = orchestrator.run(benchmark, generic, margin, strategy, my_price)
    except Exception as e:
        return jsonify({"error": f"AI recommendation failed: {str(e)}"}), 500

    prices = [c["price"] for c in competitors]
    market_avg = round(sum(prices) / len(prices), 2)
    competitor_gap = round(my_price - market_avg, 2)

    return jsonify({
        "drug": drug_info,
        "my_price": my_price,
        "target_margin": target_margin,
        "market": {
            "average": market_avg,
            "low": round(min(prices), 2),
            "high": round(max(prices), 2),
            "competitors": competitors,
        },
        "kpis": {
            "market_avg": market_avg,
            "position": benchmark["position"],
            "generic_savings_pct": generic["savings_pct"],
            "suggested_price": margin["suggested_price"],
            "margin_opportunity": margin["margin_gap"],
            "competitor_gap": competitor_gap,
        },
        "agents": {
            "benchmark": benchmark,
            "generic": generic,
            "margin": margin,
            "strategy": strategy,
        },
        "final_recommendation": final,
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    body = request.get_json(force=True)
    message = (body.get("message") or "").strip()
    context = body.get("context", {})

    if not message:
        return jsonify({"error": "Message is required."}), 400

    try:
        response = orchestrator.chat_followup(message, context)
        return jsonify({"response": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
    app.run(debug=debug, port=port)
