import time
import re
import random
from selenium.webdriver.chrome.service import Service
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys

def create_driver():
    options = Options()

    options.binary_location = "/usr/bin/google-chrome"

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--lang=es-MX")
    options.add_argument("--disable-blink-features=AutomationControlled")

    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/150.0.0.0 Safari/537.36"
    )

    service = Service(ChromeDriverManager().install())

    return webdriver.Chrome(service=service, options=options)

def login_facebook(driver, account):
    print(f"🔑 Intentando login con {account['alias']} / {account['email']}")

    driver.get("https://www.facebook.com/login")
    time.sleep(5)

    print(f"📍 URL: {driver.current_url}")
    print(f"📄 Título: {driver.title}")

    try:
        email_input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[name='email'], input#email")
            )
        )

        pass_input = WebDriverWait(driver, 30).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "input[name='pass'], input#pass")
            )
        )

        email_input.click()
        email_input.clear()
        email_input.send_keys(account["email"])

        time.sleep(1)

        pass_input.click()
        pass_input.clear()
        pass_input.send_keys(account["password"])

        time.sleep(1)

        driver.save_screenshot("/app/login_filled.png")
        print("📸 Login llenado guardado en /app/login_filled.png")

        print("🔘 Enviando login con ENTER desde password...")
        pass_input.send_keys(Keys.ENTER)

        print("⏳ Esperando respuesta...")
        time.sleep(10)
        current_url = driver.current_url.lower()
        print(f"📍 Post-login URL: {current_url}")

        driver.save_screenshot("/app/post_login.png")

        if "selfie_landing" in current_url:
            print(f"🚨 Cuenta bloqueada por selfie: {account['alias']}")
            return False

        if "checkpoint" in current_url:
            print(f"🚨 Cuenta en checkpoint: {account['alias']}")
            return False

        if "login" not in current_url:
            print(f"✅ LOGIN EXITOSO para {account['alias']}")
            return True

        print("❌ Login fallido - todavía en login")
        return False
    except Exception as e:
        print(f"💥 Error en login: {type(e).__name__}: {str(e)}")
        print(f"📍 URL actual: {driver.current_url}")

        driver.save_screenshot("/app/login_error.png")

        with open("/app/login_error.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        print("📸 Screenshot guardado en /app/login_error.png")
        print("📄 HTML guardado en /app/login_error.html")

        return False
    

def extract_whatsapp_links(text):
    patterns = [
        r"https?://chat\.whatsapp\.com/[A-Za-z0-9]+",
        r"https?://wa\.me/[0-9]+",
        r"wa\.me/[0-9]+",
        r"https?://api\.whatsapp\.com/send\?phone=[0-9]+",
    ]
    links = []
    for pattern in patterns:
        links.extend(re.findall(pattern, text, re.IGNORECASE))
    return list(set(links))


def search_groups(driver, keyword, region, max_groups):
    query = f"{keyword} {region}".strip()
    search_url = f"https://mbasic.facebook.com/search/groups/?q={query.replace(' ', '%20')}"
    
    print(f"🔍 Buscando: {search_url}")
    driver.get(search_url)
    time.sleep(5)
    
    groups = []
    scrolls = 0
    
    while len(groups) < max_groups and scrolls < 5:
        anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/groups/']")
        
        for anchor in anchors:
            href = anchor.get_attribute("href")
            name = anchor.text.strip() or "Grupo"
            
            if not href or "/groups/" not in href or "search" in href:
                continue
            
            clean_url = href.split("?")[0]
            if not any(g["group_url"] == clean_url for g in groups):
                groups.append({
                    "group_name": name[:120],
                    "group_url": clean_url,
                })
                print(f"   📁 Grupo: {name[:50]}...")
            
            if len(groups) >= max_groups:
                break
        
        if len(groups) >= max_groups:
            break
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
        scrolls += 1
    
    print(f"👥 Total grupos: {len(groups)}")
    return groups


def inspect_group(driver, group, keyword, region, account_alias):
    print(f"📖 Analizando: {group['group_name'][:50]}...")
    
    mbasic_url = group["group_url"].replace("www.facebook.com", "mbasic.facebook.com")
    driver.get(mbasic_url)
    time.sleep(4)
    
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)
    
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
        whatsapp_links = extract_whatsapp_links(body_text)
        
        if whatsapp_links:
            print(f"   ✨ Encontrados {len(whatsapp_links)} links de WhatsApp")
        else:
            print(f"   ⚠️ No se encontraron links")
    except Exception as e:
        print(f"   ⚠️ Error: {e}")
        whatsapp_links = []
    
    results = []
    for link in whatsapp_links:
        results.append({
            "accountAlias": account_alias,
            "keyword": keyword,
            "location": region,
            "groupName": group["group_name"],
            "groupUrl": group["group_url"],
            "whatsappLink": link,
            "scrapedAt": datetime.now().isoformat(timespec="seconds"),
        })
    
    return results


def scrape_with_account(account, keywords, locations, max_results, max_seconds):
    driver = create_driver()
    results = []
    started_at = time.time()
    
    try:
        ok = login_facebook(driver, account)
        if not ok:
            print(f"❌ Login fallido para {account['alias']}")
            return results
        
        for keyword in keywords:
            for region in locations or [""]:
                if time.time() - started_at >= max_seconds:
                    return results
                
                groups = search_groups(driver, keyword, region, max_results)
                
                for group in groups:
                    if time.time() - started_at >= max_seconds:
                        return results
                    
                    found = inspect_group(
                        driver, group, keyword, region, account["alias"]
                    )
                    results.extend(found)
                    
                    if len(results) >= max_results:
                        return results[:max_results]
    
    finally:
        driver.quit()
    
    return results[:max_results]


def run_scraper(accounts, keywords, locations, max_results, max_seconds, workers):
    usable_accounts = accounts[:workers]
    all_results = []
    
    if not usable_accounts:
        return all_results
    
    per_account_limit = max(1, max_results // len(usable_accounts))
    
    with ThreadPoolExecutor(max_workers=len(usable_accounts)) as executor:
        futures = [
            executor.submit(
                scrape_with_account,
                account,
                keywords,
                locations,
                per_account_limit,
                max_seconds,
            )
            for account in usable_accounts
        ]
        
        for future in as_completed(futures):
            try:
                all_results.extend(future.result())
            except Exception as e:
                print(f"🚨 Error en worker: {e}")
    
    return all_results[:max_results]