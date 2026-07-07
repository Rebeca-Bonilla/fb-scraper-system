from account_loader import load_accounts
from facebook_login import login_facebook

def test_accounts(driver):
    accounts = load_accounts()

    for account in accounts:
        email = account["email"]
        password = account["password"]

        print(f"Probando cuenta: {email}")

        success, reason = login_facebook(driver, email, password)

        if success:
            print(f"Cuenta válida: {email}")
            return account

        print(f"Falló {email}: {reason}")

    raise RuntimeError("Ninguna cuenta pudo iniciar sesión")