import time
import logging
import re
import json
import random
import string
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

chromedriver_autoinstaller.install()

class FacebookAccountFactory:
    """Crea cuentas de Facebook automáticamente"""
    
    def __init__(self):
        self.accounts = []
    
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
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def generate_email(self):
        domains = ['@10minutemail.com', '@tempmail.com', '@guerrillamail.com']
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return prefix + random.choice(domains)
    
    def generate_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choices(chars, k=12))
    
    def create_account(self):
        """Crear una cuenta de Facebook"""
        driver = self.create_driver()
        account = {
            'email': self.generate_email(),
            'password': self.generate_password(),
            'created_at': datetime.now().isoformat()
        }
        
        try:
            logger.info(f'🌸 Creando cuenta: {account["email"]}')
            driver.get('https://www.facebook.com/')
            time.sleep(2)
            
            create_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "reg")]'))
            )
            create_btn.click()
            time.sleep(2)
            
            driver.find_element(By.NAME, 'firstname').send_keys('Juan')
            driver.find_element(By.NAME, 'lastname').send_keys('Perez')
            driver.find_element(By.NAME, 'reg_email__').send_keys(account['email'])
            driver.find_element(By.NAME, 'reg_passwd__').send_keys(account['password'])
            
            driver.find_element(By.ID, 'day').send_keys('15')
            driver.find_element(By.ID, 'month').send_keys('Jun')
            driver.find_element(By.ID, 'year').send_keys('1990')
            driver.find_element(By.XPATH, '//input[@value="2"]').click()
            
            driver.find_element(By.NAME, 'websubmit').click()
            time.sleep(3)
            
            logger.info(f'✅ Cuenta creada: {account["email"]}')
            self.accounts.append(account)
            
        except Exception as e:
            logger.error(f'❌ Error creando cuenta: {e}')
        finally:
            driver.quit()
            
        return account
    
    def create_multiple_accounts(self, count=3):
        """Crear múltiples cuentas"""
        logger.info(f'🚀 Creando {count} cuentas...')
        for i in range(count):
            self.create_account()
            time.sleep(random.uniform(3, 5))
        logger.info(f'✅ Creadas {len(self.accounts)} cuentas')
        return self.accounts


class FacebookScraper:
    """Scraper de Facebook con multihilos"""
    
    def __init__(self, account_data=None):
        self.account = account_data
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
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def login_facebook(self, driver):
        if not self.account:
            return False
            
        try:
            logger.info(f'🔐 Logeando con: {self.account["email"]}')
            driver.get('https://www.facebook.com/')
            time.sleep(3)
            
            email_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, 'email'))
            )
            email_input.send_keys(self.account['email'])
            
            pass_input = driver.find_element(By.ID, 'pass')
            pass_input.send_keys(self.account['password'])
            
            login_button = driver.find_element(By.NAME, 'login')
            login_button.click()
            
            time.sleep(5)
            
            if 'login' not in driver.current_url:
                logger.info(f'✅ Login exitoso!')
                return True
            else:
                logger.error('❌ Login falló')
                return False
                
        except Exception as e:
            logger.error(f'❌ Error en login: {e}')
            return False
    
    def search_groups_internal(self, driver, keyword, location, max_results=20):
        results = []
        
        try:
            if location and location.strip():
                query = f'{keyword} {location} group whatsapp'
            else:
                query = f'{keyword} group whatsapp'
            
            search_url = f'https://www.facebook.com/search/groups?q={query.replace(" ", "%20")}'
            
            logger.info(f'🔍 Buscando: {query}')
            driver.get(search_url)
            time.sleep(5)
            
            scroll_count = 0
            while scroll_count < 3 and len(results) < max_results:
                links = driver.find_elements(By.XPATH, '//a[contains(@href, "/groups/")]')
                
                for link in links:
                    href = link.get_attribute('href')
                    text = link.text.strip()
                    
                    if href and '/groups/' in href and 'search' not in href:
                        if not any(r['group_url'] == href for r in results):
                            results.append({
                                'group_url': href,
                                'group_name': text[:100] or 'Grupo',
                                'keyword': keyword,
                                'location': location,
                                'scraped_at': datetime.now().isoformat()
                            })
                            
                            if len(results) >= max_results:
                                break
                
                driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(2)
                scroll_count += 1
                    
            logger.info(f'✅ Encontrados {len(results)} grupos para: {keyword} - {location}')
            
        except Exception as e:
            logger.error(f'❌ Error en búsqueda: {e}')
            
        return results
    
    def extract_whatsapp_from_group(self, driver, group_url):
        whatsapp_links = []
        
        try:
            logger.info(f'📖 Extrayendo WhatsApp de grupo')
            driver.get(group_url)
            time.sleep(4)
            
            driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(2)
            
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
            logger.error(f'❌ Error extrayendo WhatsApp: {e}')
            
        return whatsapp_links
    
    def scrape_with_account(self, keywords, locations, max_results=50, max_time=300):
        driver = self.create_driver()
        all_results = []
        
        try:
            if not self.login_facebook(driver):
                logger.error('❌ No se pudo loguear')
                return all_results
            
            start_time = time.time()
            
            for keyword in keywords:
                for location in locations:
                    if time.time() - start_time > max_time:
                        logger.warning('⏰ Tiempo límite alcanzado')
                        break
                        
                    groups = self.search_groups_internal(
                        driver, keyword, location, 
                        max_results // (len(keywords) * len(locations)) + 1
                    )
                    
                    for group in groups:
                        if time.time() - start_time > max_time:
                            break
                            
                        whatsapp = self.extract_whatsapp_from_group(driver, group['group_url'])
                        if whatsapp:
                            group['whatsapp_links'] = whatsapp
                            all_results.append(group)
                            
                            if len(all_results) >= max_results:
                                logger.info(f'✅ Límite de resultados alcanzado: {max_results}')
                                break
                    
                    if len(all_results) >= max_results:
                        break
                
                if len(all_results) >= max_results:
                    break
                    
        except Exception as e:
            logger.error(f'❌ Error en scraping: {e}')
        finally:
            driver.quit()
        
        logger.info(f'✅ Scraping completado: {len(all_results)} resultados')
        return all_results
    
    def scrape_all(self, keywords, locations, max_results=50, max_time=300):
        return self.scrape_with_account(keywords, locations, max_results, max_time)


def save_csv(results, filename=None):
    import csv
    from datetime import datetime
    
    if not filename:
        filename = f'resultados_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['keyword', 'location', 'group_name', 'group_url', 'whatsapp_links', 'scraped_at']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        
        for result in results:
            writer.writerow({
                'keyword': result.get('keyword', ''),
                'location': result.get('location', ''),
                'group_name': result.get('group_name', ''),
                'group_url': result.get('group_url', ''),
                'whatsapp_links': ', '.join(result.get('whatsapp_links', [])),
                'scraped_at': result.get('scraped_at', datetime.now().isoformat())
            })
    
    logger.info(f'💾 CSV guardado: {filename}')
    return filename


# ============================================
# 🔥 FUNCIÓN DE AUTOELIMINACIÓN DE CUENTAS
# ============================================

def delete_facebook_account(driver, email, password):
    """Elimina la cuenta de Facebook automáticamente"""
    try:
        logger.info(f'🗑️ Eliminando cuenta: {email}')
        
        # 1. Ir a configuración
        driver.get('https://www.facebook.com/settings')
        time.sleep(3)
        
        # 2. Ir a "Tu información en Facebook"
        driver.get('https://www.facebook.com/privacy/you/')
        time.sleep(3)
        
        # 3. Ir a "Desactivación y eliminación"
        driver.get('https://www.facebook.com/account/delete/')
        time.sleep(3)
        
        # 4. Click en "Eliminar cuenta"
        try:
            delete_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Eliminar cuenta")]')
            delete_btn.click()
            time.sleep(2)
        except:
            logger.warning('⚠️ No se encontró botón de eliminar, puede que ya esté eliminada')
            return False
        
        # 5. Confirmar con contraseña (si pide)
        try:
            password_input = driver.find_element(By.ID, 'password')
            password_input.send_keys(password)
            confirm_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Continuar")]')
            confirm_btn.click()
            time.sleep(2)
        except:
            pass
        
        # 6. Confirmar eliminación definitiva
        try:
            final_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Eliminar cuenta")]')
            final_btn.click()
            time.sleep(2)
            logger.info(f'✅ Cuenta {email} eliminada exitosamente')
            return True
        except:
            logger.warning('⚠️ No se pudo confirmar eliminación')
            return False
            
    except Exception as e:
        logger.error(f'❌ Error eliminando cuenta {email}: {e}')
        return False


def auto_delete_accounts(accounts):
    """Elimina todas las cuentas después del scraping"""
    logger.info('🗑️ Iniciando eliminación de cuentas...')
    
    for account in accounts:
        driver = None
        try:
            driver = webdriver.Chrome()
            
            # Login con la cuenta
            scraper = FacebookScraper(account)
            if scraper.login_facebook(driver):
                delete_facebook_account(driver, account['email'], account['password'])
            else:
                logger.warning(f'⚠️ No se pudo loguear para eliminar: {account["email"]}')
                
        except Exception as e:
            logger.error(f'❌ Error en eliminación: {e}')
        finally:
            if driver:
                driver.quit()
        time.sleep(3)
    
    logger.info('✅ Proceso de eliminación completado')


if __name__ == '__main__':
    print('🌸 Scraper con Selenium y Multihilos')
    print('✧･ﾟ: *✧･ﾟ:*  ﾟ･✧*:･ﾟ✧')
    
    # ============================================
    # 🔥 CONFIGURACIÓN - EL USUARIO DEFINE ESTO
    # ============================================
    
    keywords = ['ventas', 'compras', 'empleo']
    locations = ['Cancún', 'Playa del Carmen', 'Tulum']
    max_results = 50
    max_time = 300
    account_count = 3
    
    # Cambia a False si quieres mantener las cuentas
    auto_delete = True
    
    # ============================================
    # 🚀 EJECUTAR
    # ============================================
    
    print(f'\n📱 Creando {account_count} cuentas...')
    factory = FacebookAccountFactory()
    accounts = factory.create_multiple_accounts(account_count)
    
    if not accounts:
        print('❌ No se pudieron crear cuentas')
        exit(1)
    
    print(f'✅ {len(accounts)} cuentas creadas exitosamente')
    
    all_results = []
    with ThreadPoolExecutor(max_workers=len(accounts)) as executor:
        futures = []
        for i, account in enumerate(accounts):
            assigned_keywords = keywords[i::len(accounts)] if i < len(accounts) else []
            assigned_locations = locations[i::len(accounts)] if i < len(accounts) else []
            
            if assigned_keywords and assigned_locations:
                scraper = FacebookScraper(account)
                future = executor.submit(
                    scraper.scrape_with_account,
                    assigned_keywords,
                    assigned_locations,
                    max_results // len(accounts) + 1,
                    max_time // len(accounts) + 10
                )
                futures.append(future)
        
        for future in futures:
            try:
                results = future.result()
                all_results.extend(results)
            except Exception as e:
                print(f'❌ Error en hilo: {e}')
    
    if all_results:
        csv_file = save_csv(all_results)
        print(f'\n📊 TOTAL: {len(all_results)} resultados')
        print(f'💾 CSV: {csv_file}')
        
        with open('cuentas_utilizadas.json', 'w') as f:
            json.dump(accounts, f, indent=2)
        print('💾 Cuentas guardadas en cuentas_utilizadas.json')
    else:
        print('❌ No se encontraron resultados')
    
    if auto_delete and accounts:
        print('\n🗑️ Eliminando cuentas automáticamente...')
        auto_delete_accounts(accounts)
        print('✅ Cuentas eliminadas')