import json
from pathlib import Path
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

from scraper_engine import run_scraper

app = FastAPI(title="Scraper Engine")


class ScrapeRequest(BaseModel):
    jobId: str
    keywords: list[str]
    locations: list[str]
    maxResults: int = 20
    maxSeconds: int = 60
    workers: int = 1


def load_accounts():
    path = Path("accounts.local.json")

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


@app.get("/")
def health():
    return {"ok": True, "service": "scraper-engine"}


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    accounts = load_accounts()

    results = run_scraper(
        accounts=accounts,
        keywords=request.keywords,
        locations=request.locations,
        max_results=request.maxResults,
        max_seconds=request.maxSeconds,
        workers=request.workers,
    )

    for result in results:
        result["jobId"] = request.jobId

    return {
        "success": True,
        "jobId": request.jobId,
        "total": len(results),
        "results": results,
    }


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,
    )