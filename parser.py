import uiautomator2 as u2
import time
import random
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import threading

# ================== КОНФИГУРАЦИЯ (ВАША, НЕ МЕНЯЛ) ==================
FOLDER = r"C:\Git\instagram-autoreg-2026\instagram-autoreg-2026\bd"
DEVICE_SERIAL = "emulator-5554"
CHROME_PROFILE_PATH = r"C:\ChromeProfiles\MailRuAutomation"


# ================== ЧТЕНИЕ ДАННЫХ (ВАШЕ, НЕ МЕНЯЛ) ==================
def read_first_line(filename):
    path = os.path.join(FOLDER, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Файл не найден: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        first_line = f.readline().strip()
    if not first_line:
        raise ValueError(f"Первая строка пустая в файле: {filename}")
    return first_line


try:
    FULL_NAME = read_first_line("fullname.txt")
    EMAIL = read_first_line("mail.txt")
    PASSWORD = read_first_line("password.txt")
    USERNAME = read_first_line("username.txt")
    BIRTH_DATE = read_first_line("date.txt")
    day, month, year = [p.strip() for p in BIRTH_DATE.split('.')]

    print("Загружены данные для регистрации:")
    print(f"  Полное имя   : {FULL_NAME}")
    print(f"  Email        : {EMAIL}")
    print(f"  Username     : {USERNAME}")
    print(f"  Пароль       : {PASSWORD}")
    print(f"  Дата рождения: {BIRTH_DATE}  →  {day}.{month}.{year}")
except Exception as e:
    print(f"Ошибка чтения данных: {e}")
    exit(1)

# ================== ПОДКЛЮЧЕНИЕ (ВАШЕ, НЕ МЕНЯЛ) ==================
d = u2.connect(DEVICE_SERIAL)
print(f"Подключено к устройству: {DEVICE_SERIAL}")
d.implicitly_wait(6.0)


# ================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ (ВАШИ, НЕ МЕНЯЛ) ==================
def human_delay(min_sec=1.1, max_sec=3.4):
    time.sleep(random.uniform(min_sec, max_sec))


def wait_and_click(texts, timeout=18, exact=False, by_resource=None, screenshot_on_fail=True):
    start = time.time()
    while time.time() - start < timeout:
        for text in texts if isinstance(texts, list) else [texts]:
            if by_resource:
                e = d(resourceId=by_resource)
            elif exact:
                e = d(text=text)
            else:
                e = d(textContains=text)

            if e.exists:
                print(f"→ Нашли и кликаем: '{text}'")
                e.click()
                human_delay(1.3, 3.1)
                return True

        human_delay(0.6, 1.2)

    print(f"!!! Не нашли ни один из вариантов: {texts}")
    if screenshot_on_fail:
        ts = time.strftime("%Y%m%d_%H%M%S")
        path = f"fail_{ts}.png"
        d.screenshot(path)
        print(f"Скриншот ошибки сохранён: {path}")
    return False


def input_field(hint_texts, value):
    if not value:
        print("Пустое значение — пропускаем ввод")
        return

    human_delay(0.4, 1.0)

    for hint in hint_texts if isinstance(hint_texts, list) else [hint_texts]:
        if d(textContains=hint).exists:
            d(textContains=hint).click()
            human_delay(0.5, 1.2)
            break

    print(f"Вводим: {value}")
    d.send_keys(value, clear=True)
    human_delay(1.0, 2.3)


# ================== НОВАЯ ФУНКЦИЯ: ВВОД КОДА ==================
def input_code_field(code):
    """Вводит код подтверждения Instagram"""
    print(f"\n🔐 Вводим код подтверждения: {code}")

    # Ищем поле для ввода кода
    if d(textContains="Код подтверждения").exists:
        d(textContains="Код подтверждения").click()
    elif d(textContains="Confirmation code").exists:
        d(textContains="Confirmation code").click()
    else:
        # Ищем любое поле ввода
        edit_text = d(className="android.widget.EditText")
        if edit_text.exists:
            edit_text.click()

    human_delay(1, 2)
    d.send_keys(code, clear=True)
    human_delay(1, 2)

    # Нажимаем "Подтвердить" или "Далее"
    wait_and_click(["Подтвердить", "Confirm", "Далее", "Next"], timeout=10)


# ================== НОВАЯ ФУНКЦИЯ: ПОЛУЧЕНИЕ КОДА ИЗ ПОЧТЫ ==================
def get_instagram_code_from_email():
    """Запускает браузер, ждет письмо с кодом, возвращает код"""

    if not os.path.exists(CHROME_PROFILE_PATH):
        os.makedirs(CHROME_PROFILE_PATH)
        print(f"Создана папка профиля: {CHROME_PROFILE_PATH}")

    options = Options()
    options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get("https://e.mail.ru/inbox")
        print("Браузер с почтой запущен. Ожидание письма с кодом...")

        start_time = time.time()
        timeout = 120  # ждем 2 минуты

        while time.time() - start_time < timeout:
            driver.refresh()
            time.sleep(3)

            try:
                letter = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//a[.//span[contains(text(), 'is your Instagram code')]]")
                    )
                )

                letter_text = letter.text
                print(f"Найдено письмо: {letter_text}")

                import re
                match = re.search(r'\b(\d{6})\b', letter_text)
                if match:
                    code = match.group(1)
                    print(f"✅ Получен код подтверждения: {code}")
                    return code

            except:
                print(f"Ожидание кода... {int(time.time() - start_time)} сек")
                continue

        print("❌ Таймаут: код не получен")
        return None

    finally:
        driver.quit()
        print("Браузер закрыт")


# ================== ОСНОВНАЯ ЛОГИКА РЕГИСТРАЦИИ (ВАША, НЕ МЕНЯЛ) ==================
print("\nЗапуск Instagram...")
d.app_start("com.instagram.android")
human_delay(5, 9)

print("Шаг 1 → Кнопка 'Начать / Sign up / Зарегистрироваться'")
wait_and_click(["Начать", "Sign up", "Зарегистрироваться", "Create new account"])

human_delay(3, 5)
print("Шаг 2 → Выбор Email / Телефон")
wait_and_click(["Зарегистрироваться с эл. адресом"])

human_delay(3, 5)

print("Шаг 3 → Ввод email")
input_field(["Электронный адрес"], EMAIL)
wait_and_click(["Далее", "Next", "Продолжить"])
human_delay(3, 5)

code = get_instagram_code_from_email()

if code:
    input_code_field(code)
    human_delay(3, 5)
    d.screenshot("registration_complete.png")
    print("Финальный скриншот сохранён: registration_complete.png")
    print("\n✅ Регистрация завершена!")
else:
    print("\n❌ Код не получен. Регистрация не завершена.")
    d.screenshot("code_timeout.png")
    print("Скриншот ошибки: code_timeout.png")

print("Шаг 7 → Пароль")
input_field(["Пароль", "Password"], PASSWORD)
wait_and_click(["Далее", "Next", "Завершить", "Sign up", "Зарегистрироваться"])

print("Шаг 5 → Дата рождения (если появляется)")
if d(textContains="День рождения").exists or d(textContains="Birthday").exists or d(textContains="рождения").exists:
    print("→ Заполняем дату рождения")
    day_field   = d(resourceIdMatches=".*(day|Day|день).*",   className="android.widget.EditText")
    month_field = d(resourceIdMatches=".*(month|Month|месяц).*", className="android.widget.EditText")
    year_field  = d(resourceIdMatches=".*(year|Year|год).*",  className="android.widget.EditText")

    if day_field.exists:
        day_field.set_text(day)
    else:
        d.send_keys(day)

    if month_field.exists:
        month_field.set_text(month)
    else:
        d.send_keys(month)

    if year_field.exists:
        year_field.set_text(year)
    else:
        d.send_keys(year)

    human_delay(1.2, 2.5)
    wait_and_click(["Далее", "Next"])

print("Шаг 4 → Полное имя")
input_field(["Имя", "Full name", "Полное имя"], FULL_NAME)
wait_and_click(["Далее", "Next"])

print("Шаг 6 → Username")
input_field(["Имя пользователя", "Username", "Пользователь"], USERNAME)
wait_and_click(["Далее", "Next", "Проверить"])

print("\n" + "=" * 60)
print("Базовая часть регистрации завершена")
print("Ожидается экран с кодом подтверждения")
print("=" * 60)