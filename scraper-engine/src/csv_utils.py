import csv
from datetime import datetime
from pathlib import Path


DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def save_results_csv(results: list[dict]) -> str:
    filename = f"resultados_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    path = DATA_DIR / filename

    fields = [
        "account",
        "keyword",
        "region",
        "group_url",
        "whatsapp_link",
        "scraped_at",
    ]

    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(results)

    return str(path)