from parser import parse_requirements
from license_resolver import get_license
from compatibility import assess_risk

def run_scan(filepath, target_license="MIT"):
    deps = parse_requirements(filepath)
    results = []
    for dep in deps:
        lic = get_license(dep["name"])
        risk = assess_risk(target_license, lic)
        results.append({**dep, "license": lic, "risk": risk})
    return results

if __name__ == "__main__":
    for r in run_scan("sample_requirements.txt"):
        print(r)
