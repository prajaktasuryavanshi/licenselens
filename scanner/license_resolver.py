import requests

def get_license(package_name):
    url = f"https://pypi.org/pypi/{package_name}/json"
    try:
        resp = requests.get(url, timeout=10)
    except requests.RequestException:
        return "unknown"
    if resp.status_code != 200:
        return "unknown"
    info = resp.json().get("info", {})

    # newer PyPI packages use license_expression
    license_expr = (info.get("license_expression") or "").strip()
    if license_expr:
        return license_expr

    # older packages use the license field
    license_field = (info.get("license") or "").strip()
    if license_field:
        return license_field

    # fallback: check classifiers
    for classifier in info.get("classifiers", []):
        if classifier.startswith("License ::"):
            return classifier.split("::")[-1].strip()

    return "unknown"
