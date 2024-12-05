import socket

def listen_on_socket():
    # Создаем сокет
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM)
    sock.bind("/tmp/authd.sock")
    print("Listening on socket...")

    while True:
        try:
            data, addr = sock.recvfrom(1024)  # Чтение данных
            if data:
                print(f"Received data: {data.decode('utf-8')}")
        except Exception as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("Exiting...")
            break

if __name__ == "__main__":
    listen_on_socket()
