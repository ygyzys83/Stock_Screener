from config import RULES_FUNDAMENTAL as DEFAULT_RULES


def check_pe_ratio(fundamentals: dict, rules: dict) -> bool:
    rule = rules["pe_ratio"]
    val = fundamentals.get("pe_ratio")
    if val is None or val <= 0:
        return False
    return val < rule["max"]


def check_pb_ratio(fundamentals: dict, rules: dict) -> bool:
    rule = rules["pb_ratio"]
    val = fundamentals.get("pb_ratio")
    if val is None or val <= 0:
        return False
    return val < rule["max"]


def check_peg_ratio(fundamentals: dict, rules: dict) -> bool:
    rule = rules["peg_ratio"]
    val = fundamentals.get("peg_ratio")
    if val is None or val <= 0:
        return False
    return val < rule["max"]


def check_fcf_yield(fundamentals: dict, rules: dict) -> bool:
    rule = rules["fcf_yield"]
    val = fundamentals.get("fcf_yield")
    if val is None:
        return False
    return val > rule["min"]


def check_de_ratio(fundamentals: dict, rules: dict) -> bool:
    rule = rules["de_ratio"]
    val = fundamentals.get("de_ratio")
    if val is None:
        return False
    return (val / 100) < rule["max"]


def run_fundamental_checks(fundamentals: dict, rules: dict = None) -> dict:
    if rules is None:
        rules = DEFAULT_RULES
    results = {}
    rule_map = {
        "pe_ratio":  check_pe_ratio,
        "pb_ratio":  check_pb_ratio,
        "peg_ratio": check_peg_ratio,
        "fcf_yield": check_fcf_yield,
        "de_ratio":  check_de_ratio,
    }
    for rule_name, check_fn in rule_map.items():
        if rules[rule_name]["enabled"]:
            results[rule_name] = check_fn(fundamentals, rules)
    return results


def get_fundamental_values(fundamentals: dict, rules: dict = None) -> dict:
    """Returns the raw current values and thresholds for display purposes."""
    if rules is None:
        rules = DEFAULT_RULES

    pe  = fundamentals.get("pe_ratio")
    pb  = fundamentals.get("pb_ratio")
    peg = fundamentals.get("peg_ratio")
    fcf = fundamentals.get("fcf_yield")
    de  = fundamentals.get("de_ratio")

    return {
        "pe_ratio":  {
            "label":     "P/E Ratio",
            "value":     round(pe, 2)          if pe  is not None else None,
            "display":   f"{pe:.2f}"           if pe  is not None else "N/A",
            "threshold": f"< {rules['pe_ratio']['max']}",
            "passed":    rules["pe_ratio"]["enabled"] and pe is not None and pe > 0 and pe < rules["pe_ratio"]["max"],
            "enabled":   rules["pe_ratio"]["enabled"],
        },
        "pb_ratio":  {
            "label":     "P/B Ratio",
            "value":     round(pb, 2)          if pb  is not None else None,
            "display":   f"{pb:.2f}"           if pb  is not None else "N/A",
            "threshold": f"< {rules['pb_ratio']['max']}",
            "passed":    rules["pb_ratio"]["enabled"] and pb is not None and pb > 0 and pb < rules["pb_ratio"]["max"],
            "enabled":   rules["pb_ratio"]["enabled"],
        },
        "peg_ratio": {
            "label":     "PEG Ratio",
            "value":     round(peg, 2)         if peg is not None else None,
            "display":   f"{peg:.2f}"          if peg is not None else "N/A",
            "threshold": f"< {rules['peg_ratio']['max']}",
            "passed":    rules["peg_ratio"]["enabled"] and peg is not None and peg > 0 and peg < rules["peg_ratio"]["max"],
            "enabled":   rules["peg_ratio"]["enabled"],
        },
        "fcf_yield": {
            "label":     "FCF Yield",
            "value":     round(fcf * 100, 2)   if fcf is not None else None,
            "display":   f"{fcf*100:.2f}%"     if fcf is not None else "N/A",
            "threshold": f"> {rules['fcf_yield']['min']*100:.0f}%",
            "passed":    rules["fcf_yield"]["enabled"] and fcf is not None and fcf > rules["fcf_yield"]["min"],
            "enabled":   rules["fcf_yield"]["enabled"],
        },
        "de_ratio":  {
            "label":     "D/E Ratio",
            "value":     round(de / 100, 2)    if de  is not None else None,
            "display":   f"{de/100:.2f}"       if de  is not None else "N/A",
            "threshold": f"< {rules['de_ratio']['max']}",
            "passed":    rules["de_ratio"]["enabled"] and de is not None and (de / 100) < rules["de_ratio"]["max"],
            "enabled":   rules["de_ratio"]["enabled"],
        },
    }