import socket
import base64
import os
import re

HOST = '127.0.0.1'
PORT = 3335
FORMAT = 'utf-8'

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as clientsocket:
        clientsocket.connect((HOST, PORT))
        response = clientsocket.recv(1024).decode(FORMAT)
        if(response[:3] != '+OK'):
                print("Error connecting to the server")
                return

        msg = "CAPA\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "USER LarGar@hehe.com\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "PASS largar123456\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "STAT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        response = clientsocket.recv(1024).decode(FORMAT)
        pattern = re.compile(r'OK (\d+) \d+')
        nEmail = pattern.search(response).group(1)
        print(f"So email: {nEmail}\r\n")
        msg = "LIST\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "UIDL\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "RETR 5\r\n"  
        clientsocket.sendall(msg.encode(FORMAT))
        response = ""
        while True:
          chunk = clientsocket.recv(1024).decode(FORMAT)
          if not chunk:
               break
          response += chunk
          if '\r\n.\r\n' in chunk:
               break 
        lines = response.splitlines()
        boundary = '--'+lines[1].split('boundary=')[1].replace('"','')
        print(boundary)
        i=0
        filename = ""
        filedata = ""
        while i < len(lines):
             if("Date:" in lines[i] or "To:" in lines[i] or "Cc:" in lines[i] or "From:" in lines[i] or "Subject:" in lines[i]):
                  print(lines[i])
             if("Content-Transfer-Encoding: 7bit" in lines[i]):
                  i+=2
                  while True:
                       if lines[i] != '':
                            print(lines[i])
                            i+=1
                       else:
                            break
             if("Content-Disposition: attachment" in lines[i]):
                filename = lines[i].split('=')[1].strip('" ')
                i += 4  # Skip unnecessary lines
                while i < len(lines):
                    if not 'Content-Type:' in lines[i] or '' in lines[i]:
                        filedata += lines[i].replace('\r\n',"")
                        i += 1
                    elif 'Content-Type' in lines[i]:
                        i += 5
                        filename = lines[i+1].split('=')[1].strip('" ')
                        with open(os.path.join('C:\\GIALAC\\Anaconda\\test', filename), "wb") as f:
                              f.write(base64.b64decode(filedata))
                        filedata = ""
                    else:
                         with open(os.path.join('C:\\GIALAC\\Anaconda\\test', filename), "wb") as f:
                              f.write(base64.b64decode(filedata))
                         break
                
             i += 1
       
        msg = "QUIT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        

if __name__ == '__main__':
    main()

