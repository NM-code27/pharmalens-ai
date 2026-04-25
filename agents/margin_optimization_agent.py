def run(drug_info: dict, my_price: float, target_margin: float, competitor_prices: list) -> dict:
    """Suggest optimal price based on target margin and market data."""
    prices = [c["price"] for c in competitor_prices]
    avg = sum(prices) / len(prices)
    low = min(prices)

    # Estimate cost from market low (assume 60-70% of lowest price is cost)
    drug_hash = sum(ord(c) for c in drug_info.get("matched_name", "x").lower())
    cost_ratio = 0.60 + (drug_hash % 11) / 100  # 0.60–0.70
    estimated_cost = round(low * cost_ratio, 2)

    # Compute required price for target margin
    # margin = (price - cost) / price => price = cost / (1 - margin%)
    if target_margin >= 100:
        target_margin = 40
    required_price = round(estimated_cost / (1 - target_margin / 100), 2)

    # Blend between required price and market average for final suggestion
    suggested_price = round((required_price * 0.55 + avg * 0.45), 2)

    # Actual margin at suggested price
    actual_margin = round(((suggested_price - estimated_cost) / suggested_price) * 100, 1)
    current_margin = round(((my_price - estimated_cost) / my_price) * 100, 1) if my_price > 0 else 0

    margin_gap = round(actual_margin - current_margin, 1)

    if margin_gap > 5:
        insight = (f"Pricing at ${suggested_price:.2f} achieves ~{actual_margin:.1f}% margin vs "
                   f"your current ~{current_margin:.1f}%. "
                   f"Estimated cost floor: ${estimated_cost:.2f}.")
        action = f"Move price to ${suggested_price:.2f} to hit your {target_margin:.0f}% margin target."
        score = 82
    elif margin_gap < -5:
        insight = (f"Your current price yields ~{current_margin:.1f}% margin. "
                   f"Market pressure limits ideal price to ${suggested_price:.2f} ({actual_margin:.1f}% margin).")
        action = f"Accept {actual_margin:.1f}% margin at ${suggested_price:.2f} and offset with volume strategy."
        score = 55
    else:
        insight = (f"Suggested price ${suggested_price:.2f} yields {actual_margin:.1f}% margin, "
                   f"close to your {target_margin:.0f}% target. Cost floor estimated at ${estimated_cost:.2f}.")
        action = "Price is near optimal. Focus on throughput and refill adherence."
        score = 74

    return {
        "agent": "Margin Optimization",
        "icon": "📈",
        "score": score,
        "estimated_cost": estimated_cost,
        "suggested_price": suggested_price,
        "current_margin": current_margin,
        "optimal_margin": actual_margin,
        "target_margin": target_margin,
        "margin_gap": margin_gap,
        "insight": insight,
        "action": action
    }
