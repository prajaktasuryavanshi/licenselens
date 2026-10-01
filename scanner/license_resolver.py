from functools import lru_cache

import requests


@lru_cache(maxsize=256)
def get_license(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException:
        return "unknown"
    if resp.status_code != 200:
        return "unknown"
    info = resp.json().get("info", {})

    for classifier in info.get("classifiers", []):
        if classifier.startswith("License :: OSI Approved ::"):
            return classifier.split("::")[-1].strip()

    expr = (info.get("license_expression") or "").strip()
    if expr and len(expr) <= 120:
        return expr
    field = (info.get("license") or "").strip()
    if field and len(field) <= 120:
        return field
    return "unknown"
