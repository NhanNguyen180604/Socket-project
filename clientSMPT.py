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
    temp = input('To: ')
    if (temp != ''):
        email.To = list(set(re.split(', |,| ', temp)))
    
    temp = input('Cc: ')
    if (temp != ''):
        email.Cc = list(set(re.split(', |,| ', temp)))
        
    temp = input('Bcc: ')
    if (temp != ''):
        email.Bcc = list(set(re.split(', |,| ', temp)))
        
    email.Subject = input('Subject: ')
    
    print('Body:')
    while True:
        line = input()
        if (line == ''):
            break
        email.Content += line
        email.Content += '\r\n'
        
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
        
        for rcpt in list(set(email.To + email.Cc + email.Bcc)):
            msg = f'RCPT TO:<{rcpt}>\r\n'
            client.sendall(msg.encode('utf-8'))
            if (client.recv(1024).decode('utf-8')[0:3] != '250'):
                raise RuntimeError('250 reply not received from server when sending RCPT')
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        
        current_time = time.time()
        current_date = time.ctime(current_time)
        msg = 'Date: ' + current_date + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        #send data
        msg = f'From: {name_of_user} <{user}>\r\n'
        client.sendall(msg.encode('utf-8'))
        
        if (len(email.To) > 0):
            msg = 'To: '
            for i in email.To:
                msg += i + ', '

            msg = msg[:-2] + '\r\n'
            client.sendall(msg.encode('utf-8'))
        
        if (len(email.Cc)):
            msg = 'Cc: '
            for i in email.Cc:
                msg += i + ', '
                
            msg = msg[:-2] + '\r\n'
            client.sendall(msg.encode('utf-8'))
            
        msg = f'Subject: {email.Subject}\r\n\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.sendall(email.Content.encode('utf-8'))
        
        msg = '\r\n.\r\nQUIT\r\n'  #the end of mail content
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)