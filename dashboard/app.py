import json
import os
from collections import Counter
from datetime import datetime

import pandas as pd
import requests
import streamlit as st

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
ICONS = {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low", "Unknown": "⚪ Unknown"}
SAMPLE = "flask==2.0.1\nrequests==2.31.0\nnumpy\npandas\ndjango\npylint\nPyQt5\n"

st.set_page_config(page_title="LicenseLens", page_icon="🔍", layout="wide")

st.markdown(
    """
<style>
.hero {background: linear-gradient(120deg,#4f46e5,#7c3aed 55%,#06b6d4);
  padding: 2rem 2.2rem; border-radius: 18px; color: white; margin-bottom: 1.2rem;}
.hero h1 {margin:0; font-size: 2.4rem; color:white;}
.hero p {margin:.4rem 0 0; opacity:.92; font-size:1.05rem;}
.pill {display:inline-block; padding:.2rem .7rem; margin:.7rem .4rem 0 0; border-radius:99px;
  background:rgba(255,255,255,.18); font-size:.82rem;}
div[data-testid="stMetric"] {background: rgba(124,58,237,.10); border:1px solid rgba(124,58,237,.35);
  padding: .9rem 1rem; border-radius: 14px;}
</style>
<div class="hero">
  <h1>🔍 LicenseLens</h1>
  <p>Open-source dependency &amp; license compliance platform</p>
  <span class="pill">PyPI Metadata</span><span class="pill">SPDX Licenses</span>
  <span class="pill">CycloneDX SBOM</span><span class="pill">FastAPI + Streamlit + Docker</span>
</div>
""",
    unsafe_allow_html=True,
)

if "history" not in st.session_state:
    st.session_state.history = []
if "scan" not in st.session_state:
    st.session_state.scan = None

with st.sidebar:
    st.header("⚙️ Scan Settings")
    project_license = st.selectbox(
        "Your project's license",
        ["MIT", "Apache-2.0", "BSD-3-Clause", "GPL-3.0", "Proprietary"],
    )
    only_issues = st.toggle("Show only risky packages", value=False)
    st.divider()
    st.caption("Backend")
    st.code(API_URL, language=None)
    try:
        requests.get(f"{API_URL}/docs", timeout=2)
        st.success("API online")
    except Exception:
        st.error("API offline")


def run_scan(name, content):
    files = {"file": (name, content, "text/plain")}
    with st.spinner("Scanning dependencies via PyPI..."):
        resp = requests.post(
            f"{API_URL}/scan", files=files, data={"project_license": project_license}, timeout=300
        )
    if resp.status_code == 200:
        data = resp.json()
        data["file"] = name
        data["time"] = datetime.now().strftime("%d %b %H:%M")
        st.session_state.scan = data
        st.session_state.history.append(data)
    else:
        st.error("Scan failed. Is the backend running?")


tab_scan, tab_sbom, tab_hist, tab_arch = st.tabs(
    ["📤 New Scan", "📄 SBOM", "🕘 History", "🏗️ Architecture"]
)

with tab_scan:
    c1, c2 = st.columns([3, 1])
    uploaded = c1.file_uploader("Upload requirements.txt", type=["txt"])
    c2.write("")
    c2.write("")
    use_sample = c2.button("✨ Try sample project", use_container_width=True)
    if uploaded and st.button("🚀 Run License Scan", type="primary"):
        run_scan(uploaded.name, uploaded.getvalue())
    if use_sample:
        run_scan("sample_requirements.txt", SAMPLE.encode())

    scan = st.session_state.scan
    if scan:
        rows = scan["results"]
        if not rows:
            st.warning("No packages found. Upload a valid requirements.txt file.")
        else:
            df = pd.DataFrame(rows)
            counts = Counter(df["risk"])
            m = st.columns(5)
            m[0].metric("Packages", len(df))
            m[1].metric("🔴 High risk", counts.get("High", 0))
            m[2].metric("🟡 Medium", counts.get("Medium", 0))
            m[3].metric("🟢 Low", counts.get("Low", 0))
            m[4].metric("⚠️ Conflicts", int((df["status"] == "Conflict").sum()))

            conflicts = df[df["status"] == "Conflict"]
            if len(conflicts):
                names = ", ".join(conflicts["package"])
                st.error(f"License conflict: **{names}** (copyleft) inside a **{scan['project_license']}** project.")
            else:
                st.success(f"No license conflicts for a {scan['project_license']} project.")

            view = df.copy()
            view["risk"] = view["risk"].map(ICONS)
            if only_issues:
                view = view[df["status"] != "OK"]
            left, right = st.columns([3, 2])
            left.subheader("Dependencies")
            left.dataframe(view, use_container_width=True, hide_index=True)
            right.subheader("License distribution")
            right.bar_chart(df["license"].value_counts())
    else:
        st.info("Upload a requirements.txt or click **Try sample project** to see a live scan.")

with tab_sbom:
    scan = st.session_state.scan
    if scan and scan["results"]:
        sbom = {
            "bomFormat": "CycloneDX",
            "specVersion": "1.4",
            "version": 1,
            "metadata": {"timestamp": datetime.utcnow().isoformat() + "Z"},
            "components": [
                {
                    "type": "library",
                    "name": r["package"],
                    "version": r["version"],
                    "licenses": [{"license": {"name": r["license"]}}],
                }
                for r in scan["results"]
            ],
        }
        st.subheader("Software Bill of Materials (CycloneDX)")
        d1, d2 = st.columns(2)
        d1.download_button("⬇️ Download SBOM (JSON)", json.dumps(sbom, indent=2), "sbom.json", use_container_width=True)
        d2.download_button(
            "⬇️ Download report (CSV)",
            pd.DataFrame(scan["results"]).to_csv(index=False),
            "license_report.csv",
            use_container_width=True,
        )
        st.json(sbom, expanded=False)
    else:
        st.info("Run a scan first to generate the SBOM.")

with tab_hist:
    st.subheader("Saved scan history (database)")
    try:
        hist = requests.get(f"{API_URL}/history", timeout=5).json()
    except Exception:
        hist = []
    if hist:
        st.dataframe(pd.DataFrame(hist), use_container_width=True, hide_index=True)
    else:
        st.info("No saved scans yet. Run a scan and it will appear here.")

with tab_arch:
    st.subheader("Containerised architecture")
    st.graphviz_chart(
        """
digraph G {
  rankdir=LR; node [shape=box, style="rounded,filled", fillcolor="#ede9fe", fontname="Helvetica"];
  User -> Dashboard [label="upload"];
  Dashboard [label="Dashboard\\n(Streamlit :8501)"];
  API [label="API + Scanner\\n(FastAPI :8000)"];
  PyPI [label="PyPI JSON API", fillcolor="#cffafe"];
  DB [label="PostgreSQL\\n(volume)", fillcolor="#fef3c7"];
  Dashboard -> API [label="POST /scan"];
  API -> PyPI [label="license metadata"];
  API -> DB [label="save scans", style=dashed];
}
"""
    )
    st.caption("Docker Compose runs dashboard, api and db as separate containers on one network, configured via .env.")
