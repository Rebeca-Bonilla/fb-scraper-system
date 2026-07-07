import time
from pathlib import Path
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def login_facebook(driver, email, password):
    driver.get("https://www.facebook.com/login")

    wait = WebDriverWait(driver, 20)

    email_input = wait.until(
        EC.presence_of_element_located((By.ID, "email"))
    )

    password_input = wait.until(
        EC.presence_of_element_located((By.ID, "pass"))
    )

    email_input.clear()
    email_input.send_keys(email)

    password_input.clear()
    password_input.send_keys(password)

    login_button = wait.until(
        EC.element_to_be_clickable((By.NAME, "login"))
    )

    login_button.click()
    time.sleep(8)

    current_url = driver.current_url.lower()

    if "checkpoint" in current_url:
        driver.save_screenshot(str(SCREENSHOT_DIR / f"checkpoint_{email}.png"))
        return False, "checkpoint"

    if "login" in current_url:
        driver.save_screenshot(str(SCREENSHOT_DIR / f"login_failed_{email}.png"))
        return False, "login_failed"

    if "facebook.com" in current_url:
        driver.save_screenshot(str(SCREENSHOT_DIR / f"login_ok_{email}.png"))
        return True, "ok"

    driver.save_screenshot(str(SCREENSHOT_DIR / f"unknown_{email}.png"))
    return False, "unknown"