import socket
import base64
import os
import json
from email.header import decode_header
import mysql.connector
import io

def GetMessage():
    config_file = "config.json"
    config : dict
    HOST : str
    PORT : int
    FORMAT : str
    password : str
    usermail : str
    
    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        PORT = config['General']['POP3']
        FORMAT = config['General']['FORMAT']
        usermail = config['General']['usermail']
        password = config['General']['password']
        db_name = config['General']['Database']
        
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

        msg = "LIST\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        clientsocket.recv(1024)
        msg = "UIDL\r\n"
        clientsocket.sendall(msg.encode(FORMAT))
        
        response = clientsocket.recv(1024).decode(FORMAT)
        response = response.split('\r\n')[1:-2]
        
        uidlList = [line[:-4] for line in response] # format of each line is '{number} {UIDL}'
        
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        
        with mysql.connector.connect(host=HOST, user=db_user, password=db_password, database=db_name) as db:
            cursor = db.cursor()
            cursor.execute('SELECT No, UIDL from email')
            db_UIDL = [f'{i[0]} {i[1]}' for i in cursor.fetchall()]
            
            new_UIDL = [x for x in uidlList if x not in db_UIDL]
            
            for new_mail in new_UIDL:
                msg = f"RETR {new_mail.split()[0]}\r\n"
                clientsocket.sendall(msg.encode(FORMAT))
                response = io.StringIO()
                
                while True:
                    chunk = clientsocket.recv(10000).decode(FORMAT)
                    if not chunk:
                        break
                    response.write(chunk)
                    if '\r\n.\r\n' in chunk[-1000:]:
                        break
                    
                response = response.getvalue().split('\r\n', 1)[1]
                filecontent, From, Subject, Content = string_parser(response)
                folder = filter(From, Subject, Content)
                filepath = os.path.join(os.getcwd(), folder, new_mail.split()[1] + '.msg')
                
                os.makedirs(os.path.dirname(filepath),exist_ok=True)
                with open(filepath, 'w') as fi:
                    fi.write(filecontent)
                    
                # insert row into database
                command = 'INSERT INTO email VALUES (%s, %s, %s, %s, %s, %s)'
                val = (int(new_mail.split()[0]), new_mail.split()[1], From, Subject.split(maxsplit=1)[1], folder, 0)
                cursor.execute(command, val)
                db.commit() # save changes
             
        msg = "QUIT\r\n"
        clientsocket.sendall(msg.encode(FORMAT))

def CheckMail():
    config_file = 'config.json'
    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        db_name = config['General']['Database']
        
    while True:
        print("Here is the list of folders in your mailbox:")
        print("1. Inbox")
        print("2. College")
        print("3. Important")
        print("4. Spam")
        choice = input("Choose the folder (press anything else to quit): ")
        
        if (choice < "1" or choice > "4"):
            print('Quit')
            return

        folder_name = get_folder_name(int(choice))          
         
        print(f"Folder: {folder_name}")
        folderpath = os.path.join(os.getcwd(), folder_name)
        if not os.path.exists(folderpath):
            print("This file doesn't exist")
            return
        
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        with mysql.connector.connect(host=HOST, user=db_user, password=db_password, database=db_name) as db: 
            while True:
                command = 'SELECT * FROM email WHERE Folder = "' + folder_name + '"'
                cursor = db.cursor()
                cursor.execute(command)
                files = cursor.fetchall()
            
                msg = '{:<5} || {:<10} || {:<30} || {:<100}'
                print(msg.format('No', '', 'From', 'Subject'))
                for i, file in enumerate(files, start=1):
                    if (file[5] == False):
                        print(msg.format(i, '(Unread)', f'<{file[2]}>', file[3]))
                    else:
                        print(msg.format(i, '', f'<{file[2]}>', file[3]))
                                
                mail_choice = input(f'Choose email to read (1 - {i}), type "q" to quit: ')
                if mail_choice == 'q' or mail_choice == 'Q':
                    break
                
                mail_choice = int(mail_choice)
                if mail_choice < 1 or mail_choice > i:
                    print('Invalid choice')
                else:
                    command = 'UPDATE email SET IsRead = TRUE WHERE UIDL = "' + files[mail_choice - 1][1] + '"'
                    cursor.execute(command)
                    db.commit()  # save changes
                    
                    mail_dict, header, body = ReadFile(folderpath, files, mail_choice)
                    print(header + '\n\n' + body)  
                    if 'File' in mail_dict:
                        ans = input('Do you want to download attached file?: ')
                        if ans == 'Y' or ans == 'y':
                            for att in mail_dict['File']:    
                                filepath = os.path.join(os.getcwd(), 'Attachment', att[0])
                                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                                with open(filepath, 'wb') as fi:
                                    fi.write(base64.b64decode(att[1]))
                                        
def get_folder_name(folder_number):
    folders = {
        1: "Inbox",
        2: "College",
        3: "Important",
        4: "Spam",
    }
    return folders.get(folder_number, "Unknown")

def string_parser(response:str):
    email = io.StringIO()
    From = io.StringIO()
    Subject = io.StringIO()
    Content = io.StringIO()
    
    if('boundary' not in response[:50]):
        boundary = '\r\n\r\n'
    else:
        boundary = '--'+response.split('boundary="')[1].split('"\r\n')[0]
    
    part = response.split(boundary)
    header = part[0].splitlines()
    body = part[1].splitlines()

    for line in header:
        if("Date:" in line ):
            email.write(line + '\n')
        if("From" in line):
            fromLine = line.split()
            decoded = decode_header (fromLine[1])[0][0].decode(decode_header(fromLine[1])[0][1])
            email.write(fromLine[0] + ' ' + decoded + fromLine[2] + '\n')
            From.write(fromLine[2][1:-1])
        if("To:" in line or "Cc:" in line or "Bcc:" in line):
            email.write(line + '\n')
        if("Subject" in line):
            email.write(line + '\n')
            Subject.write(line) 
    
    email.write('Body:')
    
    if part[1] == '\r\n.\r\n':
        email.write('\n\n.')
        return email.getvalue(), From.getvalue(), Subject.getvalue(), Content.getvalue()

    if(boundary == '\r\n\r\n'):
        start = 0
    else:
        start = 4
    
    for line in body[start:]:
        email.write(line + '\n')
        Content.write(line)
    
    if 'Content-Type' in part[2]:
        email.write("\nFile:")
        atts = []
        atts.append(part[2].splitlines())
        for bruh in part[3:-1]:
            atts.append(bruh.splitlines())
        for att in atts: 
            filename = att[3].split('=')[1].strip('" ')
            filedata = io.StringIO()
            for line in att[5:]:
                filedata.write(line) 
            email.write(f'\n\n{filename}\n{filedata.getvalue()}')
    
    email.write('\n\n.')
    
    return email.getvalue(), From.getvalue(), Subject.getvalue(), Content.getvalue()

def ReadFile(folderpath, files, mail_choice):
    with open(os.path.join(folderpath, files[mail_choice - 1][1] + '.msg'), 'r') as fi:
        filecontent = fi.read()
        section = filecontent.split('\n\n')
        mail_dict = {}
        header = section[0].split('\nBody:', 1)[0]
        body = section[0].split('\nBody:', 1)[1]
        
        for line in header.splitlines():
            if('From' in line):
                mail_dict['From'] = line.split('<', 1)[0].split(' ', maxsplit=1)[1]
                mail_dict['MailFrom'] = line.split('<', 1)[1].split('>',1)[0]
            else:
                part = line.split(':', 1)
                mail_dict[part[0]] = part[1].strip()
        if body:
            mail_dict['Body'] = body
            
        if 'File:' in section[1]:
            mail_dict['File'] = []
            for file in section[2:-1]:
                filename = file.split('\n',1)[0]
                filedata = file.split('\n',1)[1]
                mail_dict['File'].append((filename, filedata))                  
    return mail_dict, header, body         

def filter(From:str, Subject:str, Content:str) -> str:
    
    with open('config.json', 'r') as fin:
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