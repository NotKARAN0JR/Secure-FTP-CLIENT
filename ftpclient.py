import socket
import pickle
import os
import ssl

passwords = {
    '1234': '192.168.6.32',
    '5678': '192.168.1.10',
    '7890': '192.168.32.32',
    '6789': '192.168.123.133',
    '4567': '192.168.123.32',
}

def authenticate(password):
    return passwords.get(password)

def ftp_client(hostname, port):
    try:
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        client_socket = context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=hostname)
        client_socket.connect((hostname, port))
        print("Connection established successfully.")

        password = input("Enter your password: ")
        client_socket.send(password.encode())
        auth_response = client_socket.recv(1024).decode()
        
        if auth_response == "Authenticated":
            print("Authentication successful.")
            while True:
                print("\nMenu:")
                print("1. Directory listing")
                print("2. Download a file")
                print("3. Upload a file")
                print("4. Delete a file")
                print("5. Rename a file")
                print("6. Create a directory")
                print("7. Delete a directory")
                print("8. Exit")
                choice = input("Enter your choice: ")
                client_socket.send(choice.encode())
                
                if choice == "1":
                    data = client_socket.recv(1024).decode()
                    print(data)
                elif choice == "2":
                    filename = input("Enter the filename to download: ")
                    client_socket.send(filename.encode())
                    data = client_socket.recv(1024)
                    if data.startswith(b"File does not exist."):
                        print(data.decode())
                    else:
                        with open(filename, 'wb') as f:
                            f.write(data)
                        print("File downloaded.")

                elif choice == "3":
                    filename = input("Enter the filename to upload: ")
                    if not os.path.exists(filename):
                        print("File does not exist.")
                    else:
                        client_socket.send(filename.encode())
                        with open(filename, 'rb') as f:
                            data = f.read()
                        client_socket.send(data)
                        print("File uploaded.")

                elif choice == "4":
                    filename = input("Enter the filename to delete: ")
                    client_socket.send(filename.encode())
                    data = client_socket.recv(1024).decode()
                    print(data)
                elif choice == "5":
                    old_filename = input("Enter the old filename: ")
                    new_filename = input("Enter the new filename: ")
                    client_socket.send(pickle.dumps((old_filename, new_filename)))
                    data = client_socket.recv(1024).decode()
                    print(data)
                elif choice == "6":
                    directory_name = input("Enter the directory name to create: ")
                    client_socket.send(directory_name.encode())
                    data = client_socket.recv(1024).decode()
                    print(data)
                elif choice == "7":
                    directory_name = input("Enter the directory name to delete: ")
                    client_socket.send(directory_name.encode())
                    data = client_socket.recv(1024).decode()
                    print(data)
                elif choice == "8":
                    print("Exiting FTP client.")
                    break
                else:
                    print("Invalid choice. Please enter a valid option.")
        else:
            print("Authentication failed. Exiting.")
            return
    except Exception as e:
        print(f"Error: {e}")
    finally:
        client_socket.close()

if __name__ == "__main__":
    hostname = '192.168.32.133'
    port = 21
    ftp_client(hostname, port)
