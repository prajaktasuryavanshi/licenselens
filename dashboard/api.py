import os
import re
import shutil
import uuid

import requests
from fastapi import FastAPI, Form, UploadFile

app = FastAPI(title="LicenseLens API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

COPYLEFT_PROJECTS = ("GPL", "AGPL")


def classify(lic: str) -> str:
    l = lic.upper()
    if not l or l == "UNKNOWN":
        return "Unknown"
    if "LGPL" in l or "MPL" in l or "EPL" in l or "CDDL" in l:
        return "Medium"
    if "GPL" in l:
        return "High"
    return "Low"


def pypi_lookup(name: str):
    """Fetch (license, latest_version) for a package from the PyPI JSON API."""
    try:
        r = requests.get(f"https://pypi.org/pypi/{name}/json", timeout=8)
        if r.status_code != 200:
            return "Unknown", ""
        info = r.json()["info"]
        lic = ""
        for c in info.get("classifiers", []):
            if c.startswith("License :: OSI Approved ::"):
                lic = c.split("::")[-1].strip().replace(" License", "").replace("Apache Software", "Apache-2.0")
                break
        if not lic:
            raw = (info.get("license_expression") or info.get("license") or "").strip()
            lic = raw if 0 < len(raw) <= 40 else "Unknown"
        return lic, info.get("version", "")
    except Exception:
        return "Unknown", ""


def parse_requirements(text: str):
    pkgs = []
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        if not line or line.startswith("-"):
            continue
        m = re.match(r"^([A-Za-z0-9_.\-]+)\s*(?:\[.*\])?\s*(?:[=<>!~]=?\s*([^\s;,]+))?", line)
        if m:
            pkgs.append((m.group(1), m.group(2) or ""))
    return pkgs[:40]


@app.post("/scan")
async def scan_project(file: UploadFile, project_license: str = Form("MIT")):
    scan_id = str(uuid.uuid4())
    path = f"{UPLOAD_DIR}/{scan_id}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    with open(path, encoding="utf-8", errors="ignore") as f:
        packages = parse_requirements(f.read())

    project_is_copyleft = any(k in project_license.upper() for k in COPYLEFT_PROJECTS)
    results = []
    for name, version in packages:
        lic, latest = pypi_lookup(name)
        risk = classify(lic)
        if risk == "High" and not project_is_copyleft:
            status = "Conflict"
        elif risk in ("Medium", "Unknown"):
            status = "Review"
        else:
            status = "OK"
        results.append(
            {
                "package": name,
                "version": version or latest,
                "license": lic,
                "risk": risk,
                "status": status,
            }
        )
    return {"scan_id": scan_id, "project_license": project_license, "results": results}
