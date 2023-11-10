import socket
import time
import email.message
import email.policy
import re
import os
import mimetypes
import base64

def SendMail():
    HOST = '127.0.0.1'
    PORT = 9696
    
    user = 'ntnhan@gmail.com'
    name_of_user = "Nguyen Thanh Nhan"
    
    #input Email content
    print("Enter email's detail, press enter to skip a field")
    user_email = email.message.EmailMessage(email.policy.SMTPUTF8)
    
    user_email.add_header('From', f'{name_of_user} <{user}>')
    
    temp = input('To: ')
    if (temp != ''):
        user_email.add_header('To', temp)
        
    temp = input('Cc: ')
    if (temp != ''):
        user_email.add_header('Cc', temp)
        
    temp = input('Bcc: ')
    if (temp != ''):
        user_email.add_header('Bcc', temp)
        
    user_email.add_header('Subject', input('Subject: '))
    
    print("Content:")
    content = []
    while True:
        line = input()
        if (line == ''):
            break
        content.append(line)
    
    body = ''
    for line in content:
        body += line + '\r\n'
    
    user_email.set_content(body)
    
    #input file path            
    if (input('Do you want to attach file (Y/N): ') == 'Y'):
        while True:
            input_path = input('Enter path: ')
            if (os.path.exists(input_path) and os.path.isfile(input_path)):
                if (os.path.getsize(input_path) > 3e+6):
                    print('Your file\'s size should not exceed 3MB')
                    continue
                
                mime_type, encoding = mimetypes.guess_type(input_path, strict=True)
                file_name = os.path.basename(input_path)
                
                with open(input_path, 'rb') as fi:
                    data = fi.read()
                    user_email.add_attachment(data, maintype=mime_type.split('/')[0],
                                                    subtype=mime_type.split('/')[1],
                                                    filename=file_name)
                    
                if (input('Do you want to attach another file (Y/N): ') == 'Y'):
                    continue
                break
            
            else:
                print('You entered an invalid path!')
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        #initialize TCP connection
        client.connect((HOST, PORT))
        response = client.recv(1024).decode('utf-8')
        
        if (response[:3] != '220'):
            print('220 not received from server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
            
        msg = 'EHLO [127.0.0.1]\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = f'MAIL FROM:<{user}>\r\n'
        client.sendall(msg.encode('utf-8'))
        
        recipentList = []
        if (user_email['To'] != None):
            recipentList += list(set(re.split(', |,| ', str(user_email['To']))))
        if (user_email['Cc'] != None):
            recipentList += list(set(re.split(', |,| ', str(user_email['Cc']))))
        if (user_email['Bcc'] != None):
            recipentList += list(set(re.split(', |,| ', str(user_email['Bcc']))))
        
        for rcpt in recipentList:
            msg = f'RCPT TO:<{rcpt}>\r\n'
            client.sendall(msg.encode('utf-8'))
        
        del user_email['Bcc']    
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        
        current_time = time.time()
        current_date = time.ctime(current_time)
        msg = 'Date: ' + current_date + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        #send data
        data = user_email.as_bytes(policy=email.policy.SMTPUTF8)
        client.sendall(data)
        
        #end of mail
        client.sendall(b'\r\n\r\n.\r\nQUIT\r\n')
        client.recv(1024)