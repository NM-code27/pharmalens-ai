import requests

RXNAV_BASE = "https://rxnav.nlm.nih.gov/REST"

def get_drug_info(drug_name: str) -> dict:
    """Fetch drug info from RxNav API and return structured data."""
    result = {
        "searched": drug_name,
        "matched_name": drug_name,
        "rxcui": None,
        "generic_name": None,
        "brand_name": None,
        "drug_class": None,
        "alternatives": [],
        "source": "rxnav"
    }

    try:
        resp = requests.get(
            f"{RXNAV_BASE}/drugs.json",
            params={"name": drug_name},
            timeout=8
        )
        resp.raise_for_status()
        data = resp.json()

        concept_group = data.get("drugGroup", {}).get("conceptGroup", [])
        for group in concept_group:
            concepts = group.get("conceptProperties", [])
            if not concepts:
                continue
            tty = group.get("tty", "")
            first = concepts[0]

            if result["rxcui"] is None:
                result["rxcui"] = first.get("rxcui")
                result["matched_name"] = first.get("name", drug_name)

            if tty in ("IN", "MIN", "PIN"):
                result["generic_name"] = first.get("name")
            elif tty in ("BN", "BPCK"):
                result["brand_name"] = first.get("name")

            for c in concepts[:4]:
                alt = c.get("name", "")
                if alt and alt not in result["alternatives"] and alt != result["matched_name"]:
                    result["alternatives"].append(alt)

        # Try related drugs endpoint for more generics
        if result["rxcui"]:
            try:
                rel_resp = requests.get(
                    f"{RXNAV_BASE}/rxcui/{result['rxcui']}/related.json",
                    params={"tty": "IN+MIN+BN"},
                    timeout=6
                )
                rel_data = rel_resp.json()
                rel_groups = rel_data.get("relatedGroup", {}).get("conceptGroup", [])
                for rg in rel_groups:
                    rg_tty = rg.get("tty", "")
                    rg_concepts = rg.get("conceptProperties", [])
                    if rg_concepts:
                        nm = rg_concepts[0].get("name", "")
                        if rg_tty in ("IN", "MIN") and not result["generic_name"]:
                            result["generic_name"] = nm
                        elif rg_tty == "BN" and not result["brand_name"]:
                            result["brand_name"] = nm
            except Exception:
                pass

    except requests.exceptions.ConnectionError:
        result["source"] = "fallback"
        result["generic_name"] = _fallback_generic(drug_name)
    except Exception:
        result["source"] = "fallback"
        result["generic_name"] = _fallback_generic(drug_name)

    # Fill in generic name heuristic if still missing
    if not result["generic_name"]:
        result["generic_name"] = _fallback_generic(drug_name)

    return result


def _fallback_generic(drug_name: str) -> str:
    """Known brand -> generic mappings as fallback."""
    known = {
        "lipitor": "atorvastatin",
        "zocor": "simvastatin",
        "crestor": "rosuvastatin",
        "glucophage": "metformin",
        "advil": "ibuprofen",
        "tylenol": "acetaminophen",
        "zithromax": "azithromycin",
        "amoxil": "amoxicillin",
        "augmentin": "amoxicillin/clavulanate",
        "nexium": "esomeprazole",
        "prilosec": "omeprazole",
        "synthroid": "levothyroxine",
        "norvasc": "amlodipine",
        "zoloft": "sertraline",
        "prozac": "fluoxetine",
        "plavix": "clopidogrel",
        "coumadin": "warfarin",
        "lasix": "furosemide",
        "tenormin": "atenolol",
        "lopressor": "metoprolol",
    }
    return known.get(drug_name.lower(), drug_name.lower())
