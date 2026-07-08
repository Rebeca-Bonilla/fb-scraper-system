import time
import re
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


def create_driver(account):
    alias = account["alias"]
    profile_dir = f"/app/chrome-profiles/{alias}"

    options = Options()
    options.binary_location = "/usr/bin/google-chrome"

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-software-rasterizer")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-background-networking")
    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-ipc-flooding-protection")
    options.add_argument("--disable-features=Translate,AutomationControlled")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--remote-debugging-port=0")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--lang=es-MX")

    options.add_argument(f"--user-data-dir={profile_dir}")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.set_page_load_timeout(45)

    return driver

def safe_get(driver, url, wait_seconds=6):
    try:
        driver.get(url)
    except Exception as e:
        print(f"⚠️ Error cargando URL: {url}")
        print(f"⚠️ Detalle: {e}")

    time.sleep(wait_seconds)


def check_saved_session(driver, account):
    alias = account["alias"]

    print(f"🔐 Verificando sesión guardada para {alias}")

    safe_get(driver, "https://www.facebook.com/", 8)

    current_url = driver.current_url.lower()
    driver.save_screenshot(f"/app/session_check_{alias}.png")

    print(f"📍 URL sesión {alias}: {current_url}")

    if "login" in current_url or "checkpoint" in current_url:
        print(f"❌ Sesión no válida para {alias}")
        return False

    print(f"✅ Sesión válida para {alias}")
    return True


def extract_wa_me_links(text):
    patterns = [
        r"https?://wa\.me/[0-9]{8,15}",
        r"wa\.me/[0-9]{8,15}",
    ]

    links = []

    for pattern in patterns:
        links.extend(re.findall(pattern, text, re.IGNORECASE))

    clean_links = []

    for link in links:
        link = link.strip()

        if link.startswith("wa.me"):
            link = "https://" + link

        clean_links.append(link)

    return list(set(clean_links))


def search_groups(driver, keyword, region, max_groups):
    query = f"{keyword} {region}".strip()
    encoded_query = quote(query)

    search_url = f"https://www.facebook.com/search/groups/?q={encoded_query}"

    print(f"🔍 Buscando grupos: {search_url}")

    safe_get(driver, search_url, 8)

    driver.save_screenshot("/app/search_groups.png")

    groups = []

    anchors = driver.find_elements(By.CSS_SELECTOR, "a[href*='/groups/']")
    print(f"🔗 Anchors encontrados: {len(anchors)}")

    for anchor in anchors:
        href = anchor.get_attribute("href")
        text = anchor.text.strip()

        if not href:
            continue

        if "/groups/" not in href:
            continue

        if "search" in href:
            continue

        clean_url = href.split("?")[0].rstrip("/")

        if clean_url.endswith("/groups"):
            continue

        if any(g["group_url"] == clean_url for g in groups):
            continue

        name = text

        if not name:
            try:
                card = anchor.find_element(By.XPATH, "./ancestor::div[@role='article'][1]")
                lines = [line.strip() for line in card.text.split("\n") if line.strip()]
                name = lines[0] if lines else "Grupo"
            except Exception:
                name = "Grupo"

        groups.append({
            "group_name": name[:120],
            "group_url": clean_url,
        })

        print(f"   📁 Grupo: {name[:80]}")
        print(f"      🔗 {clean_url}")

        if len(groups) >= max_groups:
            break

    print(f"👥 Total grupos: {len(groups)}")
    return groups


def inspect_group_for_wa_me(driver, group, keyword, region, account_alias):
    print(f"📖 [{account_alias}] Buscando wa.me dentro de: {group['group_name'][:60]}")

    results = []
    seen_links = set()

    search_url = f"{group['group_url']}/search/?q={quote('wa.me')}"

    print(f"   🔎 Búsqueda interna: {search_url}")

    safe_get(driver, search_url, 8)

    driver.save_screenshot(f"/app/inspect_group_search_{account_alias}.png")

    for _ in range(8):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    page_text = driver.find_element(By.TAG_NAME, "body").text
    page_html = driver.page_source

    links = []
    links.extend(extract_wa_me_links(page_text))
    links.extend(extract_wa_me_links(page_html))

    try:
        hrefs = driver.execute_script("""
            return Array.from(document.querySelectorAll('a[href]'))
                .map(a => a.href)
                .filter(Boolean);
        """)
    except Exception as e:
        print(f"   ⚠️ No se pudieron leer anchors por JS: {e}")
        hrefs = []

    for href in hrefs:
        match = re.search(r"https?://wa\.me/[0-9]{8,15}", href)
        if match:
            links.append(match.group(0))
            

    for link in links:
        link = link.strip()

        if link in seen_links:
            continue

        seen_links.add(link)

        results.append({
            "accountAlias": account_alias,
            "keyword": keyword,
            "location": region,
            "groupName": group["group_name"],
            "groupUrl": group["group_url"],
            "whatsappLink": link,
            "sourceSearch": "wa.me",
            "scrapedAt": datetime.now().isoformat(timespec="seconds"),
        })

        print(f"      ✨ [{account_alias}] wa.me encontrado: {link}")

    print(f"   📌 [{account_alias}] wa.me encontrados en grupo: {len(results)}")
    return results


def scrape_with_account(account, keywords, locations, max_results, max_seconds):
    alias = account["alias"]
    driver = create_driver(account)
    results = []
    started_at = time.time()

    try:
        if not check_saved_session(driver, account):
            return results

        for keyword in keywords:
            for region in locations or [""]:
                if time.time() - started_at >= max_seconds:
                    print(f"⏱️ [{alias}] Tiempo agotado")
                    return results[:max_results]

                groups = search_groups(driver, keyword, region, max_results)

                for group in groups:
                    if time.time() - started_at >= max_seconds:
                        print(f"⏱️ [{alias}] Tiempo agotado")
                        return results[:max_results]

                    found = inspect_group_for_wa_me(
                        driver,
                        group,
                        keyword,
                        region,
                        alias
                    )

                    results.extend(found)

                    if len(results) >= max_results:
                        return results[:max_results]

    finally:
        driver.quit()

    return results[:max_results]


def run_scraper(accounts, keywords, locations, max_results, max_seconds, workers, account_aliases=None):
    if account_aliases:
        usable_accounts = [
            account for account in accounts
            if account.get("alias") in account_aliases
        ]
    else:
        usable_accounts = accounts[:workers]

    all_results = []

    print(f"🧾 Cuentas seleccionadas: {[a.get('alias') for a in usable_accounts]}")

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

    # deduplicar por enlace + grupo
    seen = set()
    clean_results = []

    for item in all_results:
        key = (item["whatsappLink"], item["groupUrl"])
        if key in seen:
            continue
        seen.add(key)
        clean_results.append(item)

    return clean_results[:max_results]