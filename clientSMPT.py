import socket
import time
from Email import Email
import re
# import sys

def SendMail():
    HOST = '127.0.0.1'
    PORT = 9696
    
    user = 'ntnhan@gmail.com'
    
    print("Enter email's detail, press enter to skip")
    email = Email()
    
    temp = input("To: ")
    if (temp != ''):
        for i in re.split(',', temp):
            email.To.append(i)
        
    temp = input("Cc: ")
    if (temp != ''):
        for i in re.split(',', temp):
            email.Cc.append(i)
        
    temp = input("Bcc: ")
    if (temp != ''):
        for i in re.split(',', temp):
            email.Bcc.append(i)
        
    email.Subject = input("Subject: ")
    print("Content:")
    while True:
        line = input()
        if (line == ''):
            break
        else:
            email.Content.append(line)
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        #initialize TCP connection
        client.connect((HOST, PORT))
        response = client.recv(1024).decode('utf-8')
        
        if (response[:3] != '220'):
            print('220 not received from server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
        
        count = 0
        while True:
            match count:
                case 0:
                    msg = 'EHLO [127.0.0.1]\r\n'
                case 1:
                    msg = 'MAIL FROM:<' + user + '>\r\n'
                case 2:
                    for receiver in list(set(email.To + email.Cc + email.Bcc)):
                        msg = 'RCPT TO:<' + receiver + '>\r\n'
                        client.sendall(msg.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        if (response[:3] != '250'):
                            print('Error occurred while trying to send RCPT info!')
                            client.sendall('QUIT\r\n'.encode('utf-8'))
                            return
                    break
                
            client.sendall(msg.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            if (response[:3] != '250'):
                print('An error has occurred')
                client.sendall('QUIT\r\n'.encode('utf-8'))
                return
            
            count += 1
            
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        if (response[:3] != '354'):
            print('354 response not received from the server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
        
        current_time = time.time()
        current_date = time.ctime(current_time)
        
        msg = 'Date: ' + current_date + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        for to in email.To:
            msg = 'To: ' + to + '\r\n'
            client.sendall(msg.encode('utf-8'))
        
        for cc in email.Cc:
            msg = 'Cc: ' + cc + '\r\n'
            client.sendall(msg.encode('utf-8'))
            
        msg = 'From: ' + user + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'Subject: ' + email.Subject + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        for line in email.Content:
            line += '\r\n'
            client.sendall(line.encode('utf-8'))
        
        msg = '\r\n.\r\n'  #the end of mail content
        client.sendall(msg.encode('utf-8'))
        
        msg = 'QUIT\r\n'
        client.sendall(msg.encode('utf-8'))