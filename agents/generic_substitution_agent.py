def run(drug_info: dict, my_price: float, competitor_prices: list) -> dict:
    """Analyze generic vs brand savings opportunity."""
    generic_name = drug_info.get("generic_name") or drug_info.get("matched_name", "generic")
    brand_name = drug_info.get("brand_name") or drug_info.get("matched_name", "brand")
    searched = drug_info.get("searched", "").lower()
    matched = drug_info.get("matched_name", "").lower()

    # Determine if searched drug is brand or generic
    is_brand = (
        drug_info.get("brand_name") and
        (searched in brand_name.lower() or brand_name.lower() in searched)
    ) or (generic_name.lower() != matched)

    # Estimate generic price as 60-75% of brand price using hash for determinism
    drug_hash = sum(ord(c) for c in generic_name.lower())
    generic_ratio = 0.60 + (drug_hash % 16) / 100  # 0.60 – 0.75
    generic_price = round(my_price * generic_ratio, 2)

    savings = round(my_price - generic_price, 2)
    savings_pct = round((savings / my_price) * 100, 1) if my_price else 0

    avg_competitor = round(sum(c["price"] for c in competitor_prices) / len(competitor_prices), 2)

    if is_brand and savings_pct >= 20:
        insight = (f"Switching patients to {generic_name} could save them ${savings:.2f} per fill "
                   f"({savings_pct:.0f}% off). Generic penetration is high for this drug class.")
        action = (f"Stock {generic_name} prominently. Offer to counsel patients on generic equivalence. "
                  f"Price generic at ${generic_price:.2f} for maximum uptake.")
        opportunity = "HIGH"
        score = 85
    elif savings_pct >= 10:
        insight = (f"{generic_name} is available at ~${generic_price:.2f}, saving patients ${savings:.2f}. "
                   f"Generic switch incentive can drive volume.")
        action = f"Promote generic {generic_name} via signage and counseling. Bundle with refill reminder."
        opportunity = "MEDIUM"
        score = 65
    else:
        insight = (f"Generic savings opportunity is modest (${savings:.2f}). "
                   f"Focus on service and convenience differentiators instead.")
        action = "Offer loyalty points on generic purchases to maintain customer retention."
        opportunity = "LOW"
        score = 40

    return {
        "agent": "Generic Substitution",
        "icon": "💊",
        "opportunity": opportunity,
        "score": score,
        "generic_name": generic_name,
        "brand_name": brand_name,
        "generic_price": generic_price,
        "brand_price": my_price,
        "savings": savings,
        "savings_pct": savings_pct,
        "insight": insight,
        "action": action
    }
