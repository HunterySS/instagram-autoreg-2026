from ppadb.client import Client as AdbClient
import time
import random
import os

# ================== НАСТРОЙКИ ==================
FOLDER = r"E:\bd"  # путь к твоей папке (r-строка, чтобы \ не экранировались)

DEVICE_SERIAL = "emulator-5554"  # из adb devices — замени, если другой

# Координаты для 720×1280 (примерные — подгони под свой эмулятор!)
COORDS = {
    "sign_up": (360, 1000),  # "Зарегистрироваться" / Sign up
    "email_phone_choice": (360, 800),  # Выбор "Email или телефон"
    "next": (600, 1100),  # "Далее" (часто справа внизу)
    "full_name_field": (360, 600),
    "username_field": (360, 800),  # если запрашивает username
    "password_field": (360, 1000),
    "birthday_day": (200, 700),  # пример для дня рождения (клик + ввод)
    "birthday_month": (360, 700),
    "birthday_year": (520, 700),
}


# ================== ЧТЕНИЕ ТОЛЬКО ПЕРВОЙ СТРОКИ ИЗ КАЖДОГО ФАЙЛА ==================
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
    FULL_NAME   = read_first_line("fullname.txt")
    EMAIL       = read_first_line("mail.txt")
    PASSWORD    = read_first_line("password.txt")
    USERNAME    = read_first_line("username.txt")
    BIRTH_DATE  = read_first_line("date.txt")  # "27.12.2002"

    day, month, year = [p.strip() for p in BIRTH_DATE.split('.')]

    print("Данные для регистрации (первая строка каждого файла):")
    print(f"  Полное имя:   {FULL_NAME}")
    print(f"  Email:        {EMAIL}")
    print(f"  Username:     {USERNAME}")
    print(f"  Пароль:       {PASSWORD}")
    print(f"  Дата рождения: {BIRTH_DATE} → {day}.{month}.{year}")

except Exception as e:
    print(f"Ошибка при чтении первой строки: {e}")
    exit(1)


# ================== ФУНКЦИИ ADB ==================
def connect():
    client = AdbClient(host="127.0.0.1", port=5037)
    device = client.device(DEVICE_SERIAL)
    print(f"Подключено: {DEVICE_SERIAL}")
    return device


def tap(device, x, y, delay=1.2):
    device.shell(f"input tap {x} {y}")
    time.sleep(delay + random.uniform(0.4, 1.8))


def input_text(device, text):
    # Экранируем пробелы и спецсимволы
    escaped = text.replace(" ", "%s").replace("&", "\&").replace("'", "\\'")
    device.shell(f"input text '{escaped}'")
    time.sleep(1.0 + random.uniform(0.5, 1.5))


# ================== ОСНОВНАЯ ЛОГИКА РЕГИСТРАЦИИ ==================
def register_one_account():
    device = connect()

    print("Запускаем Instagram...")
    device.shell("am start -n com.instagram.android/.activity.MainTabActivity")
    time.sleep(5 + random.uniform(2, 5))   # первый экран грузится дольше

    # Шаг 1. Первый экран — большая синяя кнопка "Начать"
    print("Клик по кнопке 'Начать' (Sign up)...")
    # Координаты для 720×1280 — примерно центр синей кнопки
    # Если не сработает — подгони (обычно y = 950–1150)
    tap(device, 360, 1087, delay=2.0)

    time.sleep(5 + random.uniform(2, 4))

    # Шаг 2. Экран выбора способа регистрации → клик "Email или телефон"
    print("Выбор 'Email или телефон'...")
    # Обычно эта кнопка находится чуть ниже центра
    tap(device, 360, 590, delay=1.5)   # ← подгони под свой экран!

    time.sleep(4 + random.uniform(1, 3))

    # Шаг 3. Ввод email
    print(f"Ввод email: {EMAIL}")
    # Сначала кликаем в поле ввода (чтобы активировать клавиатуру)
    tap(device, 360, 350, delay=1.0)   # примерно середина поля email
    input_text(device, EMAIL)
    time.sleep(1.5)

    # Кнопка "Далее" (обычно справа внизу или по центру внизу)
    print("Нажимаем 'Далее' после email...")
    tap(device, 360, 400, delay=2.0)  # ← это часто координаты "Next"

    time.sleep(5 + random.uniform(2, 4))

    # Шаг 4. Полное имя
    print(f"Ввод полного имени: {FULL_NAME}")
    tap(device, 360, 500, delay=1.0)   # клик в поле имени
    input_text(device, FULL_NAME)
    time.sleep(1.5)
    tap(device, 600, 1100, delay=2.0)  # Далее

    time.sleep(4 + random.uniform(1, 3))

    # Шаг 5. Дата рождения (Instagram почти всегда запрашивает)
    print("Ввод даты рождения...")
    # Поле День
    tap(device, 200, 700, delay=1.0)
    input_text(device, day)
    time.sleep(1)

    # Поле Месяц
    tap(device, 360, 700, delay=1.0)
    input_text(device, month)
    time.sleep(1)

    # Поле Год
    tap(device, 520, 700, delay=1.0)
    input_text(device, year)
    time.sleep(1.5)

    tap(device, 600, 1100, delay=2.0)  # Далее

    time.sleep(5 + random.uniform(2, 4))

    # Шаг 6. Username
    print(f"Ввод username: {USERNAME}")
    tap(device, 360, 600, delay=1.0)   # клик в поле username
    input_text(device, USERNAME)
    time.sleep(1.5)
    tap(device, 600, 1100, delay=2.0)  # Далее

    time.sleep(4 + random.uniform(1, 3))

    # Шаг 7. Пароль
    print(f"Ввод пароля: {PASSWORD}")
    tap(device, 360, 700, delay=1.0)
    input_text(device, PASSWORD)
    time.sleep(1.5)
    tap(device, 600, 1100, delay=2.0)  # Далее / Завершить

    print("\nРегистрация дошла до этапа подтверждения.")
    print("Теперь должен прийти код на email или запрос SMS.")
    print("Скрипт завершил базовую часть. Дальше — подтверждение кода вручную или через API.")


# ================== ЗАПУСК ==================
if __name__ == "__main__":
    try:
        register_one_account()
    except Exception as e:
        print(f"Критическая ошибка: {e}")