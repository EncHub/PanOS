import socket
import os

# Функция для прослушивания сокета
def listen_socket(socket_path):
    try:
        # Создаем Unix-сокет для прослушивания
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as sock:
            sock.connect(socket_path)
            print(f"Connected to socket: {socket_path}")

            while True:
                data = sock.recv(1024)  # Получаем данные из сокета
                if data:
                    message = data.decode('utf-8')
                    print(f"Received data: {message}")  # Выводим данные в консоль

                # Ожидание команды для выхода
                user_input = input("Type 'exit' to quit: ")
                if user_input.lower() == "exit":
                    print("Exiting listener.")
                    break
    except Exception as e:
        print(f"Error in socket listener: {e}")

if __name__ == "__main__":
    socket_path = "/tmp/authd.sock"  # Замените на путь вашего сокета
    listen_socket(socket_path)
