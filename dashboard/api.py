import os
import shutil
import sys
import uuid

import psycopg2
from fastapi import FastAPI, Form, UploadFile

# Person A's scanner module (scanner/ folder) is the scanning engine
SCANNER_DIR = os.getenv(
    "SCANNER_DIR",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scanner"),
)
sys.path.insert(0, SCANNER_DIR)
from main import run_scan  # noqa: E402
from db import save_scan  # noqa: E402

app = FastAPI(title="LicenseLens API")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

RISK_MAP = {
    "high": ("High", "Conflict"),
    "medium": ("Medium", "Review"),
    "ok": ("Low", "OK"),
    "unknown": ("Unknown", "Review"),
}


@app.post("/scan")
async def scan_project(file: UploadFile, project_license: str = Form("MIT")):
    scan_id = str(uuid.uuid4())
    path = f"{UPLOAD_DIR}/{scan_id}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    raw = run_scan(path, project_license)

    if os.getenv("DATABASE_URL"):
        try:
            save_scan(file.filename, project_license, raw)
        except Exception as e:
            print("DB save failed:", e)

    results = []
    for d in raw:
        risk, status = RISK_MAP.get(str(d["risk"]).lower(), ("Unknown", "Review"))
        results.append(
            {
                "package": d["name"],
                "version": d.get("version") or "",
                "license": d["license"],
                "risk": risk,
                "status": status,
            }
        )
    return {"scan_id": scan_id, "project_license": project_license, "results": results}


@app.get("/history")
def history():
    if not os.getenv("DATABASE_URL"):
        return []
    try:
        conn = psycopg2.connect(os.environ["DATABASE_URL"])
        cur = conn.cursor()
        cur.execute(
            "SELECT to_char(s.scanned_at,'DD Mon HH24:MI'), s.project_name, s.target_license, "
            "COUNT(d.id), COALESCE(SUM(CASE WHEN d.risk='high' THEN 1 ELSE 0 END),0) "
            "FROM scans s LEFT JOIN dependencies d ON d.scan_id = s.id "
            "GROUP BY s.id ORDER BY s.id DESC LIMIT 20"
        )
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [
            {"time": r[0], "file": r[1], "project license": r[2], "packages": r[3], "conflicts": int(r[4])}
            for r in rows
        ]
    except Exception:
        return []
