import socket
import time
import Email
import re
import os
import mimetypes
import base64

def SendMail():
    HOST = '127.0.0.1'
    PORT = 9696
    
    user = 'ntnhan@gmail.com'
    name_of_user = "Nguyễn Thành Nhân"
    name_of_user = name_of_user.encode('utf-8')
    name_of_user = base64.b64encode(name_of_user).decode('utf-8')
    name_of_user = f'=?UTF-8?B?{name_of_user}?='

    email = Email.Email()
    
    #input Email content
    print("Enter email's detail, press enter to skip")
    email.To = input('To: ')
    
    email.Cc = input('Cc: ')
        
    email.Bcc = input('Bcc: ')
        
    email.Subject = input('Subject: ')
    
    print('Body:')
    email.MIME_Parts.append(Email.MyMIME())
    email.MIME_Parts[0].TextBody()
    
    while True:
        line = input()
        if (line == ''):
            break
        email.MIME_Parts[0].Content += line
        email.MIME_Parts[0].Content += '\r\n'
        
    if (input('Do you want to send attachment (Y/N): ') == 'Y'):
        while True:
            input_path = input('Enter path: ')
            if (os.path.exists(input_path) and os.path.isfile(input_path)):
                if (os.path.getsize(input_path) > 3e+6):
                    print('Your file\'s size should not exceed 3MB')
                    continue
                
                mime_type = mimetypes.guess_type(input_path, strict=True)
                file_name = os.path.basename(input_path)
                
                with open(input_path, 'rb') as fi:
                    data = fi.read()
                    data = base64.b64encode(data)
                    attachment = Email.MyMIME()
                    attachment.CreateHeader(mime_type[0], file_name)
                    attachment.Content = str(data)[2:-1]
                    attachment.Content += '\r\n'
                    email.MIME_Parts.append(attachment)
                    
                if (input('Do you want to attach another file (Y/N): ') != 'Y'):
                    break
            
            else:
                print('You entered an invalid path!')
            
    # print(email.As_String(sender_mail=user, sender_name=name_of_user))
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
        if (email.To != ''):
            recipentList += re.split(', |,| ', email.To)
        if (email.Cc != ''):
            recipentList += re.split(', |,| ', email.Cc)
        if (email.Bcc != ''):
            recipentList += re.split(', |,| ', email.Bcc)
            
        for rcpt in list(set(recipentList)):
            msg = f'RCPT TO:<{rcpt}>\r\n'
            client.sendall(msg.encode('utf-8'))
            if (client.recv(1024).decode('utf-8')[:3] != '250'):
                raise RuntimeError('250 reply not received from server when sending RCPT')
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        
        data = email.As_String(sender_mail=user, sender_name=name_of_user).encode('utf-8')
        client.sendall(data)
        
        client.recv(1024)