import json
from pathlib import Path

def load_accounts():
    path = Path("accounts.json")

    if not path.exists():
        raise FileNotFoundError("No existe scraper-engine/accounts.json")

    with path.open("r", encoding="utf-8") as file:
        accounts = json.load(file)

    valid_accounts = []

    for account in accounts:
        email = account.get("email")
        password = account.get("password")

        if email and password:
            valid_accounts.append({
                "email": email,
                "password": password
            })

    if not valid_accounts:
        raise ValueError("No hay cuentas válidas en accounts.json")

    return valid_accounts
