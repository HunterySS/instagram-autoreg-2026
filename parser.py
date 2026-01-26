import random
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ===================== НАСТРОЙКИ =====================
DRIVER_PATH = r"E:\instreg\msedgedriver.exe"

FILES = {
    "email":    r"bd\mail.txt",
    "birthdate": r"bd\date.txt",
    "fullname":  r"bd\fullname.txt",
    "password":  r"bd\password.txt",
    "username":  r"bd\username.txt"
}

OUTPUT_FILE = "created_accounts.txt"

# ===================== ФУНКЦИИ =====================
def load_list(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"Ошибка чтения {filepath}: {e}")
        return []

def get_random_account():
    data = {}
    for key, path in FILES.items():
        items = load_list(path)
        if not items:
            raise ValueError(f"Файл {path} пуст или не найден")
        data[key] = random.choice(items)
    return data

def save_account(acc):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {acc['username']} | {acc['email']} | {acc['password']} | {acc['fullname']} | {acc['birthdate']}\n"
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(f"\nАккаунт сохранён:\n{line.strip()}")

# ===================== СОЗДАНИЕ АККАУНТА =====================
def create_one_account():
    print("Запуск создания одного аккаунта...\n")

    acc = get_random_account()
    print("Данные:")
    print(f"  Email:     {acc['email']}")
    print(f"  Username:  {acc['username']}")
    print(f"  Password:  {acc['password']}")
    print(f"  Fullname:  {acc['fullname']}")
    print(f"  Birthdate: {acc['birthdate']}\n")

    options = Options()
    # options.add_argument("--headless=new")   # ← раскомментируй, когда всё заработает
    options.add_argument("--window-size=1280,900")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=ru")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    driver = webdriver.Edge(service=Service(DRIVER_PATH), options=options)
    wait = WebDriverWait(driver, 30)

    try:
        driver.get("https://www.instagram.com/accounts/emailsignup/")
        print("Страница открыта. Жду форму...")
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "input")))
        time.sleep(4)

        # 1. Email — первый input[type="text"] с autocomplete="off"
        email_field = driver.find_element(By.CSS_SELECTOR, 'input[type="text"][autocomplete="off"][inputmode="text"]')
        email_field.clear()
        email_field.send_keys(acc['email'])
        print("Email введён")
        time.sleep(2)

        # 2. Fullname — второй input[type="text"] с autocomplete="off"
        fullname_field = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][autocomplete="off"]')[1]
        fullname_field.clear()
        fullname_field.send_keys(acc['fullname'])
        print("Имя и фамилия введены")
        time.sleep(2)

        # 3. Username — input с aria-label="Имя пользователя" и type="search"
        username_field = driver.find_element(By.CSS_SELECTOR, 'input[aria-label="Имя пользователя"][type="search"]')
        username_field.clear()
        username_field.send_keys(acc['username'])
        print("Username введён")
        time.sleep(2)

        # 4. Password — третий input[type="text"] с autocomplete="off"
        password_field = driver.find_elements(By.CSS_SELECTOR, 'input[type="text"][autocomplete="off"]')[2]
        password_field.clear()
        password_field.send_keys(acc['password'])
        print("Пароль введён")
        time.sleep(2)

        # 5. Дата рождения — клик по <span> с текстом
        day, month_name, year = acc['birthdate'].split('.')

        # День
        day_span = driver.find_element(By.XPATH, f"//span[text()='{int(day)}']")
        day_span.click()
        print("День выбран")
        time.sleep(1)

        # Месяц
        month_span = driver.find_element(By.XPATH, f"//span[text()='{month_name}']")
        month_span.click()
        print("Месяц выбран")
        time.sleep(1)

        # Год
        year_span = driver.find_element(By.XPATH, f"//span[text()='{year}']")
        year_span.click()
        print("Год выбран")
        time.sleep(2)

        # 6. Кнопка "Отправить" — по тексту внутри span
        submit_button = driver.find_element(By.XPATH, "//span[text()='Отправить']/ancestor::div[@role='none']")
        submit_button.click()
        print("Кнопка 'Отправить' нажата!")
        time.sleep(8)

        # Проверка на окно кода
        if "код" in driver.page_source.lower() or "code" in driver.page_source.lower():
            print("ОТКРЫЛОСЬ ОКНО ВВОДА КОДА ПОДТВЕРЖДЕНИЯ!")
        else:
            print("Окно кода не появилось — проверь вручную")

        save_account(acc)

    except Exception as e:
        print("\nОшибка:", str(e))
        driver.save_screenshot("error.png")
        print("Скриншот сохранён как error.png")

    finally:
        driver.quit()
        print("\nГотово!\n")

if __name__ == "__main__":
    create_one_account()