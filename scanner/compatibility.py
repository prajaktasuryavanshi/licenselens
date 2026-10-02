def assess_risk(target_license, dep_license):
    d = (dep_license or "").upper()
    t = (target_license or "").upper()
    if not d or d == "UNKNOWN":
        return "unknown"
    if "GPL" in t and "LGPL" not in t:
        return "ok"
    if "LGPL" in d or "MPL" in d or "EPL" in d or "CDDL" in d:
        return "medium"
    if "GPL" in d:
        return "high"
    return "ok"
