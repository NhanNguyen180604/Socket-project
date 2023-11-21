import socket
import base64
import os
import json
from email.header import decode_header
import Email

def GetMessage():
    config_file = "SocketProgramming/config.json"
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
        nEmail = int(response.split()[1])
        msg = "LIST\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "UIDL\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        response = clientsocket.recv(1024).decode(FORMAT)
        response = response.split('\r\n')[1:-2]
        uidlList = []
        for line in response:
            uidlList.append(line.split()[1])
        while nEmail > 0:
            print(f"Email: {nEmail}")
            msg = f"RETR {nEmail}\r\n"
            clientsocket.sendall(msg.encode(FORMAT))
            response = ''
            while True:
                chunk = clientsocket.recv(10000).decode(FORMAT)
                if not chunk:
                    break
                response += chunk
                if '\r\n.\r\n' in chunk:
                    break
            response = response.split('\r\n', 1)[1]
            filecontent, From, Subject, Content = string_parser(response)
            folder = filter(From, Subject, Content)
            filepath = os.path.join(os.getcwd(),folder,uidlList[nEmail-1])
            os.makedirs(os.path.dirname(filepath),exist_ok=True)
            with open(filepath, 'w') as fi:
                fi.write(filecontent)
            nEmail -=1
        msg = "QUIT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))

def CheckMail():
    print("Here is the list of folders in your mailbox:")
    print("1. Inbox")
    print("2. College")
    print("3. Important")
    print("4. Spam")
    choice = input("Choose the folder: ")
    if choice == "":
        print("Exit")
    elif choice in ["1", "2", "3", "4"]:
        folder_name = get_folder_name(int(choice))
        print(f"Folder: {folder_name}")
        folderpath = os.path.join(os.getcwd(),folder_name)
        if not os.path.exists(folderpath):
            print("This file doesn't exist")
            return
        files = os.listdir(folderpath)
        filecontent = []
        for i,file in enumerate(files,1):
            with open(os.path.join(folderpath, file), 'r') as fi:
                From = ''
                Subject =''
                for line in fi:
                    if("From: "in line):
                        From += line.split('\n')[0]
                    if("Subject: " in line):
                        Subject += line.split('\n')[0]
                        break
            print(f"{i}. {From} | {Subject}")
        email_read=int(input("Choose the email: "))
        if email_read < 0 or email_read > i:
            print('Invalid value')
            return
        with open(os.path.join(folderpath, files[email_read-1]), 'r') as fi:
            filecontent = fi.read()
            section = filecontent.split('\n\n')
            print(section[0])
            if section[1] == 'File:':
                ans = input('Do you want to download attached file?:')
                if ans == 'Y' or ans == 'y':
                    for file in section[2:-1]:
                        filename = file.split('\n',1)[0]
                        filedata = file.split('\n',1)[1]
                        filepath = os.path.join(os.getcwd(),'Attachment',filename)
                        os.makedirs(os.path.dirname(filepath),exist_ok=True)
                        with open(filepath, 'wb') as fi:
                            fi.write(base64.b64decode(filedata))
    else:
        print("Invalid value, choose from 1-5")        
            
def get_folder_name(folder_number):
    folders = {
        1: "Inbox",
        2: "College",
        3: "Important",
        4: "Spam",
    }
    
    return folders.get(folder_number, "Unknown")
def string_parser(response:str):
    email = ''
    From = ''
    Subject = ''
    Content = ''
    
    if('boundary' not in response[:50]):
        boundary = '\r\n\r\n'
    else:
        boundary = '--'+response.split('boundary="')[1].split('"\r\n')[0]
    
    part = response.split(boundary)
    header = part[0].splitlines()
    body = part[1].splitlines()

    for line in header:
        if("Date:" in line ):
            email+=line+'\n'
        if("From" in line):
            fromLine = line.split()
            decoded = decode_header (fromLine[1]) [0][0].decode (decode_header (fromLine[1]) [0][1])
            email+=fromLine[0]+' '+decoded+fromLine[2]+'\n'
            From += fromLine[2][1:-1]
        if("To:" in line or "Cc:" in line or "Bcc:" in line):
            email+=line+'\n'
        if("Subject" in line):
            email += line+'\n'
            Subject += line 
    
    email+=('Body:\n')
    
    if part[1] == '\r\n.\r\n':
        email += '\n.'
        return email, From, Subject, Content

    if(boundary == '\r\n\r\n'):
        start=0
    else:
        start=4
    
    for line in body[start:]:
        email+=line+'\n'
        Content += line
    
    if 'Content-Type' in part[2]:
        email += "File:\n"
        atts = []
        filedata = ""
        atts.append(part[2].splitlines())
        for bruh in part[3:-1]:
            atts.append(bruh.splitlines())
        for att in atts: 
            filename = att[3].split('=')[1].strip('" ')
            filedata = ''
            for line in att[5:]:
                filedata += line 
            email+=f'\n{filename}\n{filedata}\n'
    
    email+='\n.'
    
    return email, From, Subject, Content

def filter(From:str, Subject:str, Content:str) -> str:
    
    with open('SocketProgramming/config.json', 'r') as fin:
        config = json.load(fin)
        
    #filter based on from
    from_filter = config["Filter"]["From"]
    for Folder, Keywords in from_filter.items():
        if (any(key in From for key in Keywords)):
            return Folder
        
    #filter based on subject
    subject_filter = config["Filter"]["Subject"]
    temp = Subject.lower()
    for Folder, Keywords in subject_filter.items():
        if (any(key in temp for key in Keywords)):
            return Folder
        
    #filter based on content
    content_filter = config["Filter"]["Content"]
    temp = Content.lower()
    for Folder, Keywords in content_filter.items():
        if (any(key in temp for key in Keywords)):
            return Folder
    
    return 'Inbox'

        