from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
import os

chrome_profile_path = r"C:\ChromeProfiles\MailRuAutomation"

if not os.path.exists(chrome_profile_path):
    os.makedirs(chrome_profile_path)
    print(f"Создана папка профиля: {chrome_profile_path}")

url = "https://e.mail.ru/inbox"


def find_and_open_letter(driver):
    try:
        letter = WebDriverWait(driver, 25).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[.//span[contains(text(), 'is your Instagram code')]]")
            )
        )
        code = ''
        for i in range(6):
            code += letter.text[i + 10]
        print(code)
        return True
    except Exception as e:
        print(f"Письмо не найдено или не удалось открыть: {e}")
        return False


if __name__ == '__main__':
    print("Запуск Selenium с отдельным профилем...")

    options = Options()
    options.add_argument(f"--user-data-dir={chrome_profile_path}")

    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--start-maximized")               # удобно видеть окно
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        print("Браузер запущен")
        driver.get(url)
        print(f"Открыта страница: {driver.current_url}")

        time.sleep(4)

        opened = find_and_open_letter(driver)

        if not opened:
            print("Можно вручную посмотреть, что происходит в браузере...")

        # Оставляем браузер открытым, пока не нажмёшь Enter
        input("\nНажми Enter → браузер закроется...\n")

    except Exception as e:
        print(f"Критическая ошибка: {type(e).__name__}")
        print(e)

    finally:
        if 'driver' in locals():
            driver.quit()
            print("Браузер закрыт")