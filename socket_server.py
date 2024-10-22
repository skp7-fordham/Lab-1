import socket
import threading
from datetime import datetime
from collections import defaultdict

class ChatServer:
    def __init__(self, host='0.0.0.0', port=3389):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()
        self.clients = {}
        self.client_id_counter = 0
        self.chat_history = defaultdict(list)

    def handle_client(self, conn, addr, client_id):
        print(f"Client {client_id} connected: {addr}")
        conn.sendall(f"Your ID: {client_id}\n".encode())

        while True:
            try:
                data = conn.recv(1024).decode()
                if not data:
                    break
                
                command = data.strip().split(' ', 1)
                if command[0] == "list":
                    self.list_clients(conn)
                elif command[0] == "forward" and len(command) > 1:
                    self.forward_message(client_id, command[1])
                elif command[0] == "history" and len(command) > 1:
                    self.send_history(conn, client_id, command[1])
                elif command[0] == "exit":
                    conn.sendall("Goodbye\n".encode())
                    break
                else:
                    conn.sendall("Invalid command\n".encode())
            except Exception as e:
                print(f"Error handling client {client_id}: {e}")
                break
        
        conn.close()
        del self.clients[client_id]
        print(f"Client {client_id} disconnected.")

    def list_clients(self, conn):
        active_ids = ', '.join(map(str, self.clients.keys()))
        conn.sendall(f"Active clients: {active_ids}\n".encode())

    def forward_message(self, source_id, message):
        target_id, msg_content = message.split(' ', 1)
        target_id = int(target_id)
        
        if target_id in self.clients:
            full_message = f"{source_id}: {msg_content}\n"
            self.clients[target_id].sendall(full_message.encode())
            self.chat_history[(source_id, target_id)].append(full_message)
            self.chat_history[(target_id, source_id)].append(full_message)
        else:
            self.clients[source_id].sendall("Target client not found\n".encode())

    def send_history(self, conn, client_id, target_id):
        target_id = int(target_id)
        history = self.chat_history.get((client_id, target_id), [])
        history_message = ''.join(history)
        conn.sendall(f"Chat history with {target_id}:\n{history_message}".encode())

    def start(self):
        print("Server is running...")
        while True:
            conn, addr = self.server_socket.accept()
            self.client_id_counter += 1
            self.clients[self.client_id_counter] = conn
            threading.Thread(target=self.handle_client, args=(conn, addr, self.client_id_counter)).start()

if __name__ == "__main__":
    ChatServer().start()