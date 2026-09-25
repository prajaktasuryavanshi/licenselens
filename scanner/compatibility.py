COMPATIBILITY_MATRIX = {
    "MIT": {
        "GPL-3.0": "high", "GPL-2.0": "high",
        "GPL v3": "high", "GPL v2": "high",
        "BSD-3-Clause": "ok", "Apache-2.0": "ok", "MIT": "ok",
    },
}

def assess_risk(target_license, dep_license):
    if dep_license == "unknown":
        return "unknown"
    return COMPATIBILITY_MATRIX.get(target_license, {}).get(dep_license, "medium")
