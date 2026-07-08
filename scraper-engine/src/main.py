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

    account_aliases: Optional[List[str]] = Field(default=None, alias="accountAliases")


class OpenLoginRequest(BaseModel):
    alias: str


def load_accounts():
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

    return accounts


@app.get("/")
def health():
    return {
        "status": "ok",
        "message": "Scraper engine activo"
    }


@app.get("/accounts")
def get_accounts():
    accounts = load_accounts()

    return {
        "status": "success",
        "accounts": [
            {
                "alias": account.get("alias"),
                "email": account.get("email"),
            }
            for account in accounts
        ]
    }


@app.post("/open-login")
def open_login(payload: OpenLoginRequest):
    alias = payload.alias.strip()

    if not alias:
        raise HTTPException(
            status_code=400,
            detail="Alias requerido."
        )

    profile_dir = f"/app/chrome-profiles/{alias}"

    subprocess.Popen([
        "google-chrome",
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-gpu",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile_dir}",
        "https://www.facebook.com/login"
    ], env={
        **os.environ,
        "DISPLAY": ":99"
    })

    return {
        "status": "ok",
        "message": f"Chrome abierto para login manual de {alias}",
        "profileDir": profile_dir,
    }


@app.post("/scrape")
async def handle_scrape(payload: ScrapeRequest):
    accounts = load_accounts()

    print(f"Iniciando ciclo de scraping con {len(accounts)} cuentas...")
    print(f"Workers recibidos: {payload.workers}")
    print(f"Cuentas cargadas: {[a.get('alias') for a in accounts]}")
    print(f"Cuentas seleccionadas desde frontend: {payload.account_aliases}")

    results = run_scraper(
        accounts=accounts,
        keywords=payload.keywords,
        locations=payload.locations,
        max_results=payload.max_results,
        max_seconds=payload.max_seconds,
        workers=payload.workers,
        account_aliases=payload.account_aliases,
    )

    print(f"📤 Resultados finales a devolver: {len(results)}")
    print(json.dumps(results, ensure_ascii=False, indent=2))

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