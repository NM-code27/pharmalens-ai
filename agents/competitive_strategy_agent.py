def run(drug_info: dict, my_price: float, benchmark: dict, generic: dict, margin: dict) -> dict:
    """Recommend business strategy and offer plan."""
    position = benchmark.get("position", "COMPETITIVE")
    generic_opp = generic.get("opportunity", "LOW")
    margin_gap = margin.get("margin_gap", 0)
    suggested_price = margin.get("suggested_price", my_price)

    strategies = []

    # Build strategy based on combined signals
    if position == "OVERPRICED":
        strategies.append({
            "name": "Price Match Alert",
            "emoji": "🎯",
            "description": (f"Match the lowest competitive price (${benchmark['market_low']:.2f}) "
                            f"for a limited 30-day window to recapture lost customers."),
            "impact": "HIGH"
        })

    if generic_opp in ("HIGH", "MEDIUM"):
        strategies.append({
            "name": "Generic Switch Incentive",
            "emoji": "💡",
            "description": (f"Offer $2 off next fill when patient switches to "
                            f"{generic.get('generic_name', 'generic')}. "
                            f"Saves patient ${generic.get('savings', 0):.2f} and builds loyalty."),
            "impact": "HIGH" if generic_opp == "HIGH" else "MEDIUM"
        })

    strategies.append({
        "name": "90-Day Refill Bundle",
        "emoji": "📦",
        "description": (f"Offer 90-day supply at {suggested_price * 2.7:.2f} "
                        f"(10% saving vs 3x monthly). Increases fill adherence and cash flow."),
        "impact": "MEDIUM"
    })

    strategies.append({
        "name": "Loyalty Points Program",
        "emoji": "⭐",
        "description": "Award 1 point per $1 spent. Redeem 100 points for $5 off. Drives repeat visits.",
        "impact": "MEDIUM"
    })

    if position == "UNDERPRICED":
        strategies.append({
            "name": "Margin Recovery",
            "emoji": "💰",
            "description": (f"Gradually raise price by $0.50/week toward ${suggested_price:.2f}. "
                            f"Customers rarely notice incremental increases under 5%."),
            "impact": "HIGH"
        })
    else:
        strategies.append({
            "name": "Family Pack Offer",
            "emoji": "👨‍👩‍👧",
            "description": "Bundle same medication for multiple family members at 8% group discount. "
                           "Increases basket size per visit.",
            "impact": "LOW"
        })

    # Top 3 priority actions
    high = [s for s in strategies if s["impact"] == "HIGH"]
    med = [s for s in strategies if s["impact"] == "MEDIUM"]
    low = [s for s in strategies if s["impact"] == "LOW"]
    top3 = (high + med + low)[:3]

    # Business impact summary
    monthly_fills = 120  # assumed
    price_diff = suggested_price - my_price
    monthly_impact = round(price_diff * monthly_fills, 2)
    impact_label = f"+${monthly_impact:.0f}/mo" if monthly_impact > 0 else f"${monthly_impact:.0f}/mo impact"

    insight = (f"Recommended strategy: focus on {top3[0]['name']} as primary lever. "
               f"Estimated monthly revenue impact at {monthly_fills} fills: {impact_label}.")

    return {
        "agent": "Competitive Strategy",
        "icon": "🧠",
        "score": 78,
        "strategies": strategies,
        "top3": top3,
        "monthly_impact": monthly_impact,
        "impact_label": impact_label,
        "insight": insight,
        "action": f"Launch {top3[0]['name']} this week as your primary pricing move."
    }
