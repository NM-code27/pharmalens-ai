def generate_competitor_prices(drug_name: str, base_price: float) -> list:
    """Generate deterministic competitor prices based on drug name hash."""
    # Use drug name hash for determinism (same drug = same prices every run)
    seed = sum(ord(c) * (i + 1) for i, c in enumerate(drug_name.lower()))

    def pseudo(offset, scale=1.0):
        val = ((seed + offset) * 6364136223846793005 + 1442695040888963407) % (2**32)
        return (val / (2**32)) * scale

    competitors = [
        {
            "name": "CVS Pharmacy",
            "icon": "🏪",
            "base_mult": 1.12 + pseudo(1, 0.15),
            "offer": _pick_offer(seed + 1),
            "margin_base": 28,
        },
        {
            "name": "Walgreens",
            "icon": "🟦",
            "base_mult": 1.08 + pseudo(2, 0.12),
            "offer": _pick_offer(seed + 2),
            "margin_base": 26,
        },
        {
            "name": "Walmart Pharmacy",
            "icon": "🛒",
            "base_mult": 0.82 + pseudo(3, 0.10),
            "offer": _pick_offer(seed + 3),
            "margin_base": 18,
        },
        {
            "name": "Costco Pharmacy",
            "icon": "📦",
            "base_mult": 0.78 + pseudo(4, 0.08),
            "offer": _pick_offer(seed + 4),
            "margin_base": 15,
        },
        {
            "name": "Local Pharmacy",
            "icon": "🏥",
            "base_mult": 1.02 + pseudo(5, 0.14),
            "offer": _pick_offer(seed + 5),
            "margin_base": 32,
        },
        {
            "name": "Online Discount",
            "icon": "💻",
            "base_mult": 0.72 + pseudo(6, 0.12),
            "offer": _pick_offer(seed + 6),
            "margin_base": 12,
        },
    ]

    result = []
    market_base = base_price if base_price > 0 else _estimate_base(drug_name)

    for c in competitors:
        price = round(market_base * c["base_mult"], 2)
        margin = round(c["margin_base"] + pseudo(seed, 8) - 4, 1)

        if c["base_mult"] > 1.10:
            position = "premium"
        elif c["base_mult"] < 0.85:
            position = "discount"
        else:
            position = "competitive"

        result.append({
            "name": c["name"],
            "icon": c["icon"],
            "price": price,
            "offer": c["offer"],
            "margin": margin,
            "position": position,
        })

    return result


def _pick_offer(seed: int) -> str:
    offers = [
        "No current offer",
        "5% off with loyalty card",
        "$4 generic program",
        "Buy 2 get 10% off",
        "Free delivery over $30",
        "90-day supply discount",
        "Senior 10% discount",
        "First fill free",
        "Coupon: save $3",
        "Price match guarantee",
    ]
    return offers[seed % len(offers)]


def _estimate_base(drug_name: str) -> float:
    """Rough price estimate when user doesn't provide one."""
    known = {
        "lipitor": 22.50, "atorvastatin": 8.00, "metformin": 5.50,
        "ibuprofen": 4.00, "aspirin": 3.50, "amoxicillin": 12.00,
        "lisinopril": 7.00, "simvastatin": 9.00, "omeprazole": 11.00,
        "levothyroxine": 13.00, "amlodipine": 8.50, "sertraline": 10.00,
        "azithromycin": 15.00, "prednisone": 9.00, "gabapentin": 14.00,
    }
    return known.get(drug_name.lower(), 15.00)
