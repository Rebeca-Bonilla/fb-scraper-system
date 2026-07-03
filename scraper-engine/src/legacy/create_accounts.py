import time
import random
import string
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json

class AccountCreator:
    def __init__(self):
        self.accounts = []
    
    def generate_email(self):
        """Genera un correo temporal aleatorio"""
        domains = ['@tempmail.com', '@guerrillamail.com', '@10minutemail.com']
        prefix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
        return prefix + random.choice(domains)
    
    def generate_password(self):
        """Genera una contraseña segura"""
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choices(chars, k=12))
    
    def create_driver(self):
        options = Options()
        options.add_argument('--headless=new')  # Sin interfaz gráfica
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=options)
        return driver
    
    def create_account(self):
        """Crea una cuenta de Facebook con correo temporal"""
        driver = self.create_driver()
        account = {
            'email': self.generate_email(),
            'password': self.generate_password()
        }
        
        try:
            print(f'🌱 Creando cuenta: {account["email"]}')
            driver.get('https://www.facebook.com/')
            time.sleep(2)
            
            # Click en "Crear cuenta"
            create_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[contains(@href, "reg")]'))
            )
            create_btn.click()
            time.sleep(2)
            
            # Llenar formulario
            driver.find_element(By.NAME, 'firstname').send_keys('Juan')
            driver.find_element(By.NAME, 'lastname').send_keys('Perez')
            driver.find_element(By.NAME, 'reg_email__').send_keys(account['email'])
            driver.find_element(By.NAME, 'reg_passwd__').send_keys(account['password'])
            
            # Fecha de nacimiento
            driver.find_element(By.ID, 'day').send_keys('15')
            driver.find_element(By.ID, 'month').send_keys('Jun')
            driver.find_element(By.ID, 'year').send_keys('1990')
            
            # Género
            driver.find_element(By.XPATH, '//input[@value="2"]').click()
            
            # Enviar formulario
            driver.find_element(By.NAME, 'websubmit').click()
            time.sleep(3)
            
            print(f'✅ Cuenta creada: {account["email"]}')
            self.accounts.append(account)
            
            # Guardar en archivo
            self.save_accounts()
            
        except Exception as e:
            print(f'❌ Error creando cuenta: {e}')
        finally:
            driver.quit()
        
        return account
    
    def create_multiple_accounts(self, count=3):
        """Crea múltiples cuentas"""
        print(f'🚀 Creando {count} cuentas...')
        for i in range(count):
            self.create_account()
            time.sleep(random.uniform(3, 5))  # Espera entre cuentas
        print(f'✅ Creadas {len(self.accounts)} cuentas')
        return self.accounts
    
    def save_accounts(self, filename='cuentas_creadas.json'):
        """Guarda las cuentas en un archivo JSON"""
        with open(filename, 'w') as f:
            json.dump(self.accounts, f, indent=2)
        print(f'💾 Cuentas guardadas en {filename}')
    
    def load_accounts(self, filename='cuentas_creadas.json'):
        """Carga cuentas desde un archivo JSON"""
        try:
            with open(filename, 'r') as f:
                self.accounts = json.load(f)
            print(f'📂 Cargadas {len(self.accounts)} cuentas')
            return self.accounts
        except FileNotFoundError:
            print('⚠️ No se encontró el archivo de cuentas')
            return []

if __name__ == '__main__':
    print('🌸 Creador de Cuentas de Facebook')
    print('✧･ﾟ: *✧･ﾟ:*  ﾟ･✧*:･ﾟ✧')
    
    creator = AccountCreator()
    
    # Crear 2 cuentas
    accounts = creator.create_multiple_accounts(2)
    
    print('\n📋 Cuentas creadas:')
    for acc in accounts:
        print(f"  - Email: {acc['email']}")
        print(f"    Pass:  {acc['password']}")