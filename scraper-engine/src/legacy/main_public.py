import time
import logging
import re
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chromedriver_autoinstaller.install()

class PublicFacebookScraper:
    """Scraper público SIN necesidad de cuentas"""
    
    def create_driver(self):
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def search_groups(self, keyword, location, max_results=20):
        """Buscar grupos usando Google (público)"""
        driver = self.create_driver()
        results = []
        
        try:
            if location and location.strip():
                query = f'{keyword} {location} facebook group'
            else:
                query = f'{keyword} facebook group'
            
            search_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
            
            logger.info(f'🔍 Buscando: {keyword} en {location}')
            driver.get(search_url)
            time.sleep(3)
            
            links = driver.find_elements(By.XPATH, '//a[contains(@href, "facebook.com/groups")]')
            
            for link in links[:max_results]:
                try:
                    href = link.get_attribute('href')
                    if href and 'groups' in href:
                        clean_url = re.search(r'https://www.facebook.com/groups/[^&]+', href)
                        if clean_url:
                            group_url = clean_url.group(0)
                            logger.info(f'📖 Visitando grupo: {group_url}')
                            
                            whatsapp_links = self.extract_whatsapp_from_group(group_url)
                            if whatsapp_links:
                                results.append({
                                    'keyword': keyword,
                                    'location': location,
                                    'group_url': group_url,
                                    'whatsapp_links': whatsapp_links,
                                    'scraped_at': datetime.now().isoformat()
                                })
                except Exception as e:
                    logger.error(f'❌ Error extrayendo: {e}')
                    
        except Exception as e:
            logger.error(f'❌ Error en búsqueda: {e}')
        finally:
            driver.quit()
            
        return results
    
    def extract_whatsapp_from_group(self, group_url):
        """Extraer WhatsApp de un grupo público"""
        driver = self.create_driver()
        whatsapp_links = []
        
        try:
            driver.get(group_url)
            time.sleep(3)
            
            page_text = driver.find_element(By.TAG_NAME, 'body').text
            
            patterns = [
                r'https?://chat\.whatsapp\.com/[A-Za-z0-9]+',
                r'https?://wa\.me/[0-9]+',
                r'whatsapp\.com/[A-Za-z0-9]+',
                r'wa\.me/[0-9]+',
                r'https?://api\.whatsapp\.com/send\?phone=[0-9]+',
                r'\+[0-9]{10,15}',
                r'[0-9]{10,15}'
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, page_text, re.IGNORECASE)
                whatsapp_links.extend(matches)
            
            whatsapp_links = list(set(whatsapp_links))
            whatsapp_links = [w for w in whatsapp_links if len(re.sub(r'\D', '', w)) >= 10]
            
            logger.info(f'✅ Encontrados {len(whatsapp_links)} enlaces WhatsApp')
            
        except Exception as e:
            logger.error(f'❌ Error: {e}')
        finally:
            driver.quit()
            
        return whatsapp_links


def save_csv(results, filename=None):
    import csv
    from datetime import datetime
    
    if not filename:
        filename = f'resultados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['keyword', 'location', 'group_url', 'whatsapp_links', 'scraped_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'keyword': result.get('keyword', ''),
                'location': result.get('location', ''),
                'group_url': result.get('group_url', ''),
                'whatsapp_links': ', '.join(result.get('whatsapp_links', [])),
                'scraped_at': result.get('scraped_at', datetime.now().isoformat())
            })
    
    logger.info(f'💾 CSV guardado: {filename}')
    return filename


if __name__ == '__main__':
    print('🌸 Scraper PÚBLICO - Sin Cuentas')
    print('✧･ﾟ: *✧･ﾟ:*  ﾟ･✧*:･ﾟ✧')
    
    # ============================================
    # CONFIGURACIÓN (EL USUARIO DEFINE ESTO)
    # ============================================
    
    keywords = ['ventas', 'compras']
    locations = ['Cancún', 'Playa del Carmen']
    
    # ============================================
    # EJECUTAR
    # ============================================
    
    scraper = PublicFacebookScraper()
    all_results = []
    
    for keyword in keywords:
        for location in locations:
            results = scraper.search_groups(keyword, location, max_results=10)
            all_results.extend(results)
            time.sleep(2)
    
    if all_results:
        csv_file = save_csv(all_results)
        print(f'\n📊 TOTAL: {len(all_results)} resultados')
        print(f'💾 CSV: {csv_file}')
        for r in all_results[:5]:
            print(f"  - {r['keyword']} | {r['location']} | {len(r.get('whatsapp_links', []))} enlaces")
    else:
        print('❌ No se encontraron resultados')