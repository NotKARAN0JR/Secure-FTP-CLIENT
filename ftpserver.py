import socket
import threading
import os
import pickle
import ssl

passwords = {
    '1234': '192.168.6.32',
    '5678': '192.168.1.11',
    '7890': '192.168.32.32',
    '6789': '192.168.123.133',
    '4567': '192.168.123.32',
    '1357': '10.30.203.133'
}

def authenticate(password, ip):
    return passwords.get(password) == ip

def ftp_directory_listing():
    files = os.listdir()
    return "\n".join(files)

def ftp_download(client_socket, filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'rb') as f:
                data = f.read()
            client_socket.send(data)
            return "File downloaded."
        else:
            client_socket.send(b"File does not exist.")
            return "File does not exist."
    except Exception as e:
        return f"Error downloading file: {e}"

def ftp_upload(client_socket, filename):
    try:
        data = client_socket.recv(1024)
        with open(filename, 'wb') as f:
            f.write(data)
        return "File uploaded."
    except Exception as e:
        return f"Error uploading file: {e}"

def ftp_delete(filename):
    if os.path.exists(filename):
        os.remove(filename)
        return "File deleted."
    else:
        return "File does not exist."

def ftp_rename(old_filename, new_filename):
    if os.path.exists(old_filename):
        os.rename(old_filename, new_filename)
        return "File renamed."
    else:
        return "File does not exist."

def ftp_create_directory(directory_name):
    if not os.path.exists(directory_name):
        os.mkdir(directory_name)
        return "Directory created."
    else:
        return "Directory already exists."

def ftp_delete_directory(directory_name):
    if os.path.exists(directory_name):
        os.rmdir(directory_name)
        return "Directory deleted."
    else:
        return "Directory does not exist."

def handle_client(client_socket, client_ip):
    try:
        password = client_socket.recv(1024).decode()
        if authenticate(password, client_ip):
            client_socket.send("Authenticated".encode())
            print(f"Authenticated client: {client_ip}")
            while True:
                choice = client_socket.recv(1024).decode()
                if choice == "8":
                    break
                
                if choice == "1":
                    response = ftp_directory_listing()
                elif choice == "2":
                    filename = client_socket.recv(1024).decode()
                    response = ftp_download(client_socket,filename)
                elif choice == "3":
                    filename = client_socket.recv(1024).decode()
                    response = ftp_upload(client_socket,filename)
                elif choice == "4":
                    filename = client_socket.recv(1024).decode()
                    response = ftp_delete(filename)
                elif choice == "5":
                    data = client_socket.recv(1024)
                    old_filename, new_filename = pickle.loads(data)
                    response = ftp_rename(old_filename, new_filename)
                elif choice == "6":
                    directory_name = client_socket.recv(1024).decode()
                    response = ftp_create_directory(directory_name)
                elif choice == "7":
                    directory_name = client_socket.recv(1024).decode()
                    response = ftp_delete_directory(directory_name)
                else:
                    response = "Invalid choice. Please enter a valid option."
                
                client_socket.send(response.encode())
        else:
            client_socket.send("Authentication failed".encode())
            print(f"Authentication failed for client: {client_ip}")
            return
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

def start_ftp_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("192.168.32.133", 21))  
    server_socket.listen(5)
    print("Server started, waiting for connections...")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection established with {addr[0]}:{addr[1]}")

        # Wrap the client socket with an SSL context that disables certificate verification
        ssl_client_socket = ssl.wrap_socket(client_socket, server_side=True, cert_reqs=ssl.CERT_NONE)
        
        client_thread = threading.Thread(target=handle_client, args=(ssl_client_socket, addr[0]))
        client_thread.start()

if _name_ == "_main_":
    start_ftp_server()
