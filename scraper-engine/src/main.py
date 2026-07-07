import json
import os
import uvicorn
import subprocess

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional

from scraper_engine import run_scraper

app = FastAPI()


class ScrapeRequest(BaseModel):
    job_id: Optional[str] = Field(default=None, alias="jobId")
    keywords: List[str]
    locations: Optional[List[str]] = []

    max_results: int = Field(default=20, alias="maxResults")
    max_seconds: int = Field(default=600, alias="maxSeconds")
    workers: int = 2


@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Scraper engine activo"
    }

@app.post("/open-login")
def open_login():
    subprocess.Popen([
        "google-chrome",
        "--no-sandbox",
        "--user-data-dir=/app/chrome-profile",
        "--profile-directory=Default",
        "https://www.facebook.com/login"
    ], env={
        **os.environ,
        "DISPLAY": ":99"
    })

    return {
        "status": "ok",
        "message": "Chrome abierto para login manual"
    }

@app.post("/scrape")
async def handle_scrape(payload: ScrapeRequest):
    accounts_path = os.path.join(os.path.dirname(__file__), "../accounts.local.json")

    if not os.path.exists(accounts_path):
        raise HTTPException(
            status_code=500,
            detail="Archivo accounts.local.json no encontrado."
        )

    with open(accounts_path, "r", encoding="utf-8") as f:
        accounts = json.load(f)

    if not accounts:
        raise HTTPException(
            status_code=400,
            detail="No hay cuentas configuradas en el sistema."
        )

    print(f"Iniciando ciclo de scraping con {len(accounts)} cuentas...")
    print(f"Workers recibidos: {payload.workers}")
    print(f"Cuentas cargadas: {[a.get('alias') for a in accounts]}")

    results = run_scraper(
        accounts=accounts,
        keywords=payload.keywords,
        locations=payload.locations,
        max_results=payload.max_results,
        max_seconds=payload.max_seconds,
        workers=payload.workers
    )

    return {
        "status": "success",
        "jobId": payload.job_id,
        "results": results
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )