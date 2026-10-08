# LicenseLens
Open-source dependency and license compliance platform. Upload a `requirements.txt`, and LicenseLens fetches each package's license from PyPI, flags risky or conflicting licenses against your project's own license, and generates a CycloneDX SBOM and a CSV compliance report.

Built as a containerised multi-service app using Docker Compose.

## Problem Statement

Open-source projects often use third-party dependencies without checking license compatibility. This creates legal and compliance risk, for example a GPL library inside an MIT project. Checking each package by hand does not scale, and customers and auditors now ask for a Software Bill of Materials (SBOM).

## Features

- Reads `requirements.txt`
- Fetches each package's license from the PyPI JSON API
- Classifies risk as High, Medium, Low or Unknown
- Detects license conflicts against the project's own license
- Streamlit dashboard with metrics, dependency table and license chart
- Exports a CycloneDX SBOM (JSON) and a CSV compliance report
- Stores scan history in PostgreSQL

## Risk Rules

| Risk | Licenses |
|---|---|
| High | GPL, AGPL |
| Medium | LGPL, MPL, EPL |
| Low | MIT, BSD, Apache |
| Conflict | High-risk license inside a non-copyleft project |
| Review | Unknown or missing license metadata |

## Architecture

Three containers run on one Docker Compose network:

| Service | Description | Port |
|---|---|---|
| `dashboard` | Streamlit user interface | 8501 |
| `api` | FastAPI backend with the scanner module inside it | 8000 |
| `db` | PostgreSQL database with a persistent volume | 5432 |

Flow: User uploads `requirements.txt` in the dashboard, the dashboard calls the API `/scan` endpoint, the scanner looks up licenses from the PyPI JSON API, the risk engine classifies them, and results are shown in the dashboard and saved to the database.

## Project Structure

```
licenselens/
├── .github/workflows/   # GitHub Actions CI (runs tests on every push)
├── dashboard/           # Streamlit app (app.py), FastAPI (api.py), Dockerfiles, tests
├── scanner/             # Scanner module: license resolver and compatibility check
├── db_init/             # Database schema initialisation
├── samples/             # Sample requirements files for demo
├── docker-compose.yml
├── .env.example
└── README.md
```

## Run with Docker (recommended)

```bash
git clone https://github.com/prajaktasuryavanshi/licenselens.git
cd licenselens
cp .env.example .env
docker compose up --build
```

Then open:
- Dashboard: http://localhost:8501
- API docs: http://localhost:8000/docs

## Run locally (without Docker)

```bash
cd dashboard
pip install -r requirements.txt
uvicorn api:app --reload
streamlit run app.py
```

## Run tests

```bash
cd dashboard
pytest
```

Tests also run automatically on every push through GitHub Actions.

## Tech Stack

FastAPI, Uvicorn, Streamlit, PostgreSQL, Docker, Docker Compose, Git and GitHub, GitHub Actions, Pandas, pytest

## Licensing Concepts Applied

MIT, Apache-2.0, BSD, GPL, LGPL, SPDX identifiers, SBOM (CycloneDX)

## Dataset

PyPI package license metadata via the public API `https://pypi.org/pypi/<package>/json`. License reference: SPDX License List (https://spdx.org/licenses/).

## Team

- Sanobar Shaikh (PRN: 25030421039)
- Prajakta Suryavanshi (PRN: 25030421029)

Symbiosis Institute of AI, BSc AI, Batch 2026

## License

This project is released under the MIT License.
