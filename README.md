# instagram-autoreg-2026

Инструмент для автоматизации шагов регистрации в Android-приложении Instagram через ADB и (опционально) получения кода подтверждения из Mail.ru.

## Что улучшено

- Конфигурация вынесена в `config.json` (есть шаблон `config.example.json`).
- Данные аккаунта читаются из папки `bd` с проверкой формата.
- Добавлен CLI: можно переопределять путь к данным, устройство, ожидания.
- Логи и обработка ошибок стали понятнее.
- Получение email-кода вынесено в переиспользуемую функцию `GetCode.main.get_instagram_code`.

## Структура

- `parser.py` - основной ADB-флоу регистрации.
- `GetCode/main.py` - получение 6-значного кода из Mail.ru через Selenium.
- `bd/*.txt` - входные данные (берется первая строка каждого файла).
- `config.example.json` - пример конфигурации координат и параметров.

## Подготовка

1. Установите Python 3.10+.
2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Скопируйте шаблон и настройте под себя:

```bash
copy config.example.json config.json
```

4. Подготовьте файлы в `bd`:
- `fullname.txt`
- `mail.txt`
- `password.txt`
- `username.txt`
- `date.txt` в формате `DD.MM.YYYY`

## Запуск

Базовый запуск:

```bash
python parser.py
```

С переопределением устройства и данных:

```bash
python parser.py --device-serial emulator-5554 --data-dir ./bd
```

С попыткой автоматически получить код из Mail.ru и ввести его:

```bash
python parser.py --fetch-email-code --mail-profile "C:\\ChromeProfiles\\MailRuAutomation" --mail-timeout 120
```

Только получение кода из почты:

```bash
python GetCode/main.py --timeout 120
```

## Важно

- Автоматизация интерфейса может ломаться при изменении экранов приложения.
- Для получения кода через Mail.ru в профиле Chrome должна быть сохранена авторизация.
