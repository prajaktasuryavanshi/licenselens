from fastapi import FastAPI, UploadFile
import shutil
import uuid
import os

app = FastAPI()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


@app.post("/scan")
async def scan_project(file: UploadFile):
    scan_id = str(uuid.uuid4())
    path = f"{UPLOAD_DIR}/{scan_id}_{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"scan_id": scan_id, "status": "file received", "path": path}
