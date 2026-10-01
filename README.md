# LicenseLens

Detects open-source license conflicts in project dependencies and generates a CycloneDX SBOM. Containerized with Docker Compose.

## Services
- **api**: FastAPI backend, fetches license data from the PyPI JSON API
- **dashboard**: Streamlit UI
- **scanner**: scanning module (Person A)

## Run locally
    cd dashboard
    pip install -r requirements.txt
    uvicorn api:app --reload
    streamlit run app.py

## Run with Docker
    docker compose up --build
