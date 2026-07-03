import time
import re
import csv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

class PublicScraper:
    """Scraper que busca grupos de Facebook SIN necesidad de cuenta"""
    
    def __init__(self):
        self.results = []
    
    def create_driver(self):
        options = Options()
        options.add_argument('--headless=new')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return webdriver.Chrome(options=options)
    
    def search_groups(self, keyword, location, max_results=20):
        """Busca grupos usando Google (público)"""
        driver = self.create_driver()
        results = []
        
        try:
            query = f'{keyword} {location} facebook group whatsapp'
            search_url = f'https://www.google.com/search?q={query.replace(" ", "+")}'
            
            print(f'🔍 Buscando: {keyword} en {location}')
            driver.get(search_url)
            time.sleep(3)
            
            links = driver.find_elements(By.XPATH, '//a[contains(@href, "facebook.com/groups")]')
            
            for link in links[:max_results]:
                try:
                    href = link.get_attribute('href')
                    if href and '/groups/' in href:
                        clean_url = re.search(r'https://www.facebook.com/groups/[^&]+', href)
                        if clean_url:
                            group_url = clean_url.group(0)
                            print(f'📖 Visitando: {group_url}')
                            
                            whatsapp_links = self.extract_whatsapp_from_group(group_url)
                            if whatsapp_links:
                                results.append({
                                    'keyword': keyword,
                                    'location': location,
                                    'group_url': group_url,
                                    'whatsapp_links': whatsapp_links
                                })
                                print(f'✅ Encontrados {len(whatsapp_links)} enlaces')
                except Exception as e:
                    print(f'⚠️ Error en grupo: {e}')
                    
        except Exception as e:
            print(f'❌ Error: {e}')
        finally:
            driver.quit()
        
        return results
    
    def extract_whatsapp_from_group(self, group_url):
        """Visita el grupo y extrae enlaces de WhatsApp"""
        driver = self.create_driver()
        whatsapp_links = []
        
        try:
            driver.get(group_url)
            time.sleep(5)
            
            body = driver.find_element(By.TAG_NAME, 'body')
            page_text = body.text
            
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
            
        except Exception as e:
            print(f'⚠️ Error extrayendo: {e}')
        finally:
            driver.quit()
        
        return whatsapp_links
    
    def scrape_all(self, keywords, locations, max_results=10):
        """Scrapea todas las combinaciones"""
        all_results = []
        
        for keyword in keywords:
            for location in locations:
                results = self.search_groups(keyword, location, max_results)
                all_results.extend(results)
                time.sleep(2)
        
        return all_results


def save_csv(results, filename='resultados_publicos.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['keyword', 'location', 'group_url', 'whatsapp_links'])
        for result in results:
            writer.writerow([
                result['keyword'],
                result['location'],
                result['group_url'],
                ', '.join(result['whatsapp_links'])
            ])
    print(f'💾 CSV guardado: {filename}')


if __name__ == '__main__':
    print('🌸 Scraper Público (Sin cuentas, sin API, sin teléfono)')
    print('✧･ﾟ: *✧･ﾟ:*  ﾟ･✧*:･ﾟ✧')
    
    scraper = PublicScraper()
    
    keywords = ['ventas', 'compras', 'empleo']
    locations = ['Cancún', 'Playa del Carmen', 'Tulum']
    
    results = scraper.scrape_all(keywords, locations, max_results=10)
    
    if results:
        save_csv(results)
        print(f'\n📊 TOTAL: {len(results)} grupos con WhatsApp')
        for r in results[:5]:
            print(f"  - {r['keyword']} | {r['location']} | {len(r['whatsapp_links'])} enlaces")
    else:
        print('❌ No se encontraron resultados')