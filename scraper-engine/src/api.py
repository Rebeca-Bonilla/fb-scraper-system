from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from src.schemas import ScrapeRequest
from src.scraper_engine import run_scraper
from src.csv_utils import save_results_csv


app = FastAPI(title="FB Scraper System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

last_csv_path = None


@app.get("/")
def root():
    return {"status": "ok", "message": "API activa"}


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    global last_csv_path

    accounts = [account.model_dump() for account in request.accounts]

    results = run_scraper(
        accounts=accounts,
        keyword=request.keyword,
        region=request.region,
        max_results=request.max_results,
        max_seconds=request.max_seconds,
        workers=request.workers,
    )

    last_csv_path = save_results_csv(results)

    return {
        "status": "completed",
        "total_results": len(results),
        "csv_path": last_csv_path,
        "results": results,
    }


@app.get("/download")
def download():
    if not last_csv_path:
        return {"error": "No hay CSV generado"}

    return FileResponse(
        last_csv_path,
        media_type="text/csv",
        filename=last_csv_path.replace("data\\", "").replace("data/", ""),
    )