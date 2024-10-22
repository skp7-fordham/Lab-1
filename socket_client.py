import socket

def main():
    host = '34.171.53.140'
    port = 3389

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((host, port))
        print(client_socket.recv(1024).decode())  # Receive client ID

        while True:
            command = input("Enter command (list, forward, history, exit): ")
            client_socket.sendall(command.encode())
            response = client_socket.recv(1024).decode()
            print(response)

            if command.startswith("exit"):
                break

if __name__ == "__main__":
    main()
    