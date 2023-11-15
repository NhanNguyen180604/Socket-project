import socket
import base64
import os
import json
import re

def CheckMail():
    config_file = "config.json"
    config : dict
    HOST : str
    PORT : int
    FORMAT : str
    password : str
    usermail : str
    username : str
    
    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        PORT = config['General']['POP3']
        FORMAT = config['General']['FORMAT']
        usermail = config['General']['usermail']
        username = config['General']['username']
        password = config['General']['password']
        
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
        clientsocket.connect((HOST, PORT))
        response = clientsocket.recv(1024).decode(FORMAT)
        if(response[:3] != '+OK'):
                print("Error connecting to the server")
                return
        msg = "CAPA\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = f"USER {usermail}\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = f"PASS {password}\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "STAT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        response = clientsocket.recv(1024).decode(FORMAT)
        pattern = re.compile(r'OK (\d+) \d+')
        nEmail = int(pattern.search(response).group(1))
        msg = "LIST\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "UIDL\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        
        while nEmail > 0:
            print(f"Email: {nEmail}")
            msg = f"RETR {nEmail}\r\n"
            clientsocket.sendall(msg.encode(FORMAT))
            response = ""
            while True:
                chunk = clientsocket.recv(1024).decode(FORMAT)
                if not chunk:
                    break
                response += chunk
                if '\r\n.\r\n' in chunk:
                    break
            boundary = '--'+response.split('boundary="')[1].split('"\r\n')[0]
            part = response.split(boundary)
            header = part[0].splitlines()
            body = part[1].splitlines()
            for line in header:
                if("Date:" in line or "To:" in line or "Cc:" in line or "From:" in line or "Subject:" in line):
                    print(line.split('+0700')[0])   
            print(f'\r\nBody:')
            for line in body[4:]:
                print(line)
            atts = []
            filedata = ""
            if 'Content-Type' in part[2]:
                atts.append(part[2].splitlines())
                for bruh in part[3:-1]:
                    atts.append(bruh.splitlines())
            for att in atts: 
                filename = att[2].split('=')[1].strip('" ')
                for line in att[5:]:
                    filedata += line
                with open(os.path.join('C:\\GIALAC\\Anaconda\\test', filename), "wb") as f:
                    f.write(base64.b64decode(filedata))            
                    filedata = "" 
            nEmail -= 1
            print('---------------------')
        msg = "QUIT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
