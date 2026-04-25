def run(drug_info: dict, my_price: float, competitor_prices: list) -> dict:
    """Compare user price vs market and return benchmark analysis."""
    prices = [c["price"] for c in competitor_prices]
    avg = round(sum(prices) / len(prices), 2)
    low = round(min(prices), 2)
    high = round(max(prices), 2)

    diff_from_avg = round(my_price - avg, 2)
    pct_diff = round((diff_from_avg / avg) * 100, 1) if avg else 0

    if pct_diff > 12:
        position = "OVERPRICED"
        severity = "high"
        insight = (f"Your price of ${my_price:.2f} is {abs(pct_diff):.1f}% above market average (${avg:.2f}). "
                   f"Customers may switch to {_cheapest_name(competitor_prices)} at ${low:.2f}.")
        action = f"Reduce price by ${abs(diff_from_avg):.2f} or highlight added value to justify premium."
        score = 38
    elif pct_diff < -12:
        position = "UNDERPRICED"
        severity = "medium"
        insight = (f"Your price of ${my_price:.2f} is {abs(pct_diff):.1f}% below market average (${avg:.2f}). "
                   f"You are leaving margin on the table.")
        action = f"Consider raising price to ${avg:.2f} to capture missed margin without losing customers."
        score = 62
    else:
        position = "COMPETITIVE"
        severity = "low"
        insight = (f"Your price of ${my_price:.2f} is within {abs(pct_diff):.1f}% of market average (${avg:.2f}). "
                   f"You are competitively positioned.")
        action = "Maintain price and focus on service quality and loyalty programs."
        score = 88

    return {
        "agent": "Price Benchmark",
        "icon": "📊",
        "position": position,
        "severity": severity,
        "score": score,
        "market_avg": avg,
        "market_low": low,
        "market_high": high,
        "diff_from_avg": diff_from_avg,
        "pct_diff": pct_diff,
        "insight": insight,
        "action": action
    }


def _cheapest_name(competitors: list) -> str:
    return min(competitors, key=lambda x: x["price"])["name"]
