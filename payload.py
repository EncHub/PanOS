import subprocess
import sys

# Функция для установки необходимого пакета
def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Устанавливаем requests, если он не установлен
try:
    import requests
except ImportError:
    install('requests')

# Токен вашего бота
bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
# Chat ID, куда отправлять сообщение (можно узнать через getUpdates API)
chat_id = '-1002252120859'
# Сообщение, которое нужно отправить
message = 'Hello, this is a test message!'

# Формирование URL для Telegram API
url = f'https://api.telegram.org/bot{bot_token}/sendMessage'

# Параметры запроса
params = {
    'chat_id': chat_id,
    'text': message
}

# Отправка POST-запроса без проверки сертификатов
response = requests.post(url, params=params, verify=False)

# Проверка успешности
if response.status_code == 200:
    print("Message sent successfully!")
else:
    print(f"Failed to send message. Status code: {response.status_code}")
