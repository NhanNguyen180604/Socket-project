import socket

HOST = '127.0.0.1'
PORT = 9696

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientSocket:
        clientSocket.connect((HOST, PORT))
        response = clientSocket.recv(1024).decode('utf-8')
        
        if response[:3] != '220':
            print("Error connecting to the server")
            return

        print("Server: " + response)
            
        msg = "EHLO [127.0.0.1]\r\n"
        clientSocket.sendall(msg.encode('utf-8'))
        
        response = clientSocket.recv(1024).decode('utf-8')
        print(response)
        
        msg = "QUIT\r\n"
        clientSocket.send(msg.encode('utf-8'))
            
            
if __name__ == '__main__':
    main()