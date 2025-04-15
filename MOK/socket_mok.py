import socket
import threading

def handle_client(client_socket):
    with client_socket:
        print("Client connected:", client_socket.getpeername())
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break
                print(f"Received: {data.decode('utf-8')}")
                client_socket.sendall(data)
            except ConnectionResetError:
                break
def run_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', port))
    server.listen(5)
    print(f"Server listening on port {port}")
    while True:
        client_socket, addr = server.accept()
        print(f"Accepted connection from {addr} on port {port}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    ports = [8234, 9235]
    threads = []
    for port in ports:
        thread = threading.Thread(target=run_server, args=(port,))
        thread.start()
        threads.append(thread)
    for thread in threads:
        thread.join()