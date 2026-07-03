import time
import re
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from fake_useragent import UserAgent

class PublicFacebookScraper:
    def __init__(self):
        self.driver = None

    def init_driver(self):
        """Inicializa Chrome con esteroides anti-timeout y sin imágenes"""
        options = Options()
        options.add_argument('--headless=new')  # Modo oculto indispensable para multihilos
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-notifications')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        # ⚡ ESTRATEGIA DE CARGA RÁPIDA: No espera scripts de rastreo ni imágenes pesadas
        options.page_load_strategy = 'eager'

        # 🚫 BLOQUEO DE IMÁGENES: Reduce drásticamente el uso de CPU por cada hilo
        prefs = {
            "profile.managed_default_content_settings.images": 2,
            "profile.default_content_setting_values.notifications": 2
        }
        options.add_experimental_option("prefs", prefs)
        options.add_argument('--blink-settings=imagesEnabled=false')

        # User-Agent aleatorio para evitar bloqueos por firmas automatizadas
        ua = UserAgent()
        options.add_argument(f'--user-agent={ua.chrome}')

        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # ⏱️ PARED ANTI-CONGELAMIENTO: Máximo 15 segundos esperando respuesta del renderizador
        self.driver.set_page_load_timeout(15)
        self.driver.implicitly_wait(3)

    def discover_public_groups(self, keyword, location, max_groups=8):
            """Busca grupos públicos usando el bypass mbasic para evitar el muro de login"""
            query = f"{keyword} {location}"
            # Forzamos la versión mbasic móvil que tiene menos restricciones públicas
            search_url = f"https://mbasic.facebook.com/search/groups/?q={query.replace(' ', '%20')}"
            group_urls = []

            try:
                self.driver.get(search_url)
                time.sleep(2)

                # En mbasic las URLs de los grupos se ven un poco diferentes, adaptamos el XPath
                # Buscamos enlaces que apunten a /groups/ dentro del diseño móvil básico
                elements = self.driver.find_elements(By.XPATH, '//a[contains(@href, "/groups/")]')
                
                for elem in elements:
                    try:
                        href = elem.get_attribute('href')
                        if href:
                            # Limpiar y convertir la URL de mbasic a la versión web normal para el CSV
                            clean_match = re.search(r'/groups/([^/?]+)', href)
                            if clean_match:
                                group_id = clean_match.group(1)
                                url_normal = f"https://www.facebook.com/groups/{group_id}/"
                                if url_normal not in group_urls and group_id != 'home':
                                    group_urls.append(url_normal)
                        if len(group_urls) >= max_groups:
                            break
                    except:
                        continue

                print(f"📌 Encontrados {len(group_urls)} grupos para {keyword} - {location}")
            except TimeoutException:
                print(f"❌ Error en búsqueda (Timeout de Renderizado): {keyword} en {location}.")
            except Exception as e:
                print(f"⚠️ Error inesperado buscando {keyword} en {location}: {e}")

            return group_urls[:max_groups]
    def extract_whatsapp_links(self, group_url, max_seconds=25):
            """Visita el grupo en su versión ligera mbasic para extraer los links al instante"""
            whatsapp_links = []
            try:
                # Convertimos la URL normal a mbasic para un raspado ultra veloz y limpio
                mbasic_url = group_url.replace("www.facebook.com", "mbasic.facebook.com")
                self.driver.get(mbasic_url)
                time.sleep(2)

                end_time = time.time() + max_seconds
                while time.time() < end_time:
                    body = self.driver.find_element(By.TAG_NAME, 'body')
                    page_text = body.text

                    patterns = [
                        r'https?://chat\.whatsapp\.com/[A-Za-z0-9]+',
                        r'https?://wa\.me/[0-9]+',
                        r'https?://api\.whatsapp\.com/send\?phone=[0-9]+'
                    ]

                    for pattern in patterns:
                        matches = re.findall(pattern, page_text, re.IGNORECASE)
                        whatsapp_links.extend(matches)

                    # En mbasic el scroll tradicional no funciona igual porque no hay scroll infinito,
                    # pero podemos intentar buscar el enlace de "Ver más publicaciones" si existiera,
                    # o simplemente conformarnos con la primera página que suele tener los posts recientes.
                    try:
                        # Intentar dar click en "Ver más mensajes/publicaciones" si aparece abajo
                        self.driver.find_element(By.XPATH, '//div[contains(@id,"see_more_")]/a').click()
                        time.sleep(2)
                    except:
                        break # Si no hay botón de ver más, terminamos la extracción de este grupo

                whatsapp_links = list(set(whatsapp_links))
            except TimeoutException:
                print(f"⚠️ Error en grupo (Timeout): {group_url[:40]}...")
            except Exception as e:
                print(f"⚠️ Error analizando el grupo {group_url[:40]}: {e}")

            return whatsapp_links
    def close(self):
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass

def worker_thread_task(keyword, location, max_groups, max_seconds):
    """Función independiente que ejecuta cada hilo individual en aislamiento"""
    scraper = PublicFacebookScraper()
    scraper.init_driver()
    results = []

    print(f"🔍 Buscando: {keyword} en {location}")
    group_urls = scraper.discover_public_groups(keyword, location, max_groups)

    for url in group_urls:
        links = scraper.extract_whatsapp_links(url, max_seconds)
        if links:
            results.append({
                "keyword": keyword,
                "location": location,
                "group_url": url,
                "whatsapp_links": links,
                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })

    scraper.close()
    return results

def main():
    print("🌸 Scraper Público MULTIHILOS Optimizado")
    print("✧･ﾟ: *✧･ﾟ:* ﾟ･✧*:･ﾟ✧")

    # Matrices de búsqueda solicitadas
    keywords = ["ventas", "compras", "empleo"]
    locations = ["Cancún", "Playa del Carmen", "Tulum"]
    
    max_groups_per_target = 8
    max_seconds_per_group = 25
    max_threads = 4  # Ajusta según los núcleos de tu procesador (Recomendado: 3 o 4)

    all_combinations = [(kw, loc) for kw in keywords for loc in locations]
    final_leads = []

    print(f"🚀 Iniciando {len(all_combinations)} tareas distribuidas en {max_threads} hilos paralelos...")

    # Ejecución concurrente real usando la piscina de hilos nativa de Python
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = {
            executor.submit(worker_thread_task, kw, loc, max_groups_per_target, max_seconds_per_group): (kw, loc)
            for kw, loc in all_combinations
        }

        for future in as_completed(futures):
            kw, loc = futures[future]
            try:
                data = future.result()
                if data:
                    final_leads.extend(data)
            except Exception as exc:
                print(f"❌ El hilo asignado a '{kw} en {loc}' generó una excepción: {exc}")

    # Consolidar los resultados capturados en un archivo CSV limpio
    if final_leads:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"data/leads_publicos_{timestamp}.csv"
        
        import os
        os.makedirs("data", exist_ok=True)

        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Keyword', 'Location', 'Group URL', 'WhatsApp Links', 'Extraction Date'])
            for lead in final_leads:
                writer.writerow([
                    lead['keyword'],
                    lead['location'],
                    lead['group_url'],
                    ', '.join(lead['whatsapp_links']),
                    lead['date']
                ])
        print(f"\n✨ ¡Extracción Completada! Archivo CSV exportado con éxito en: {output_file}")
    else:
        print("\n❌ El ciclo terminó pero no se encontraron enlaces válidos de WhatsApp en esta tanda.")

if __name__ == "__main__":
    main()