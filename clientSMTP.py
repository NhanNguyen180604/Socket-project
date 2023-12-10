import socket
import Email
import json
import re

def send_mail(email: Email.Email):
    mail_content = email.As_Byte()    
    config_file = 'config.json'

    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        PORT = config['General']['SMTP']
        usermail = config['Account']['usermail']
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        #initialize TCP connection
        client.connect((HOST, PORT))
        response = client.recv(1024).decode('utf-8')
        if (response[:3] != '220'):
            print('220 not received from server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
            
        msg = f'EHLO [{HOST}]\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)      
        if (response[:3] != '220'):
            print('220 not received from server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
               
        msg = f'MAIL FROM:<{usermail}>\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)       
        if (response[:3] != '220'):
            print('220 not received from server!')
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
        
        recipentList = []
        if (email.To != b''):
            recipentList += re.split(b',|, | ', email.To)
        if (email.Cc != b''):
            recipentList += re.split(b',|, | ', email.Cc)
        if (email.Bcc != b''):
            recipentList += re.split(b',|, | ', email.Bcc)
            
        recipentList = [i for i in list(set(recipentList)) if i != b'']
        if recipentList == []:
            client.sendall('QUIT\r\n'.encode('utf-8'))
            return
        
        for rcpt in list(set([i for i in recipentList if i != b''])):
            msg = b'RCPT TO:<' + rcpt + b'>\r\n'
            client.sendall(msg)
            response = client.recv(1024).decode('utf-8')
            if (response[:3] != '250'):
                raise RuntimeError('Error sending RCPT')
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        if (response[:3] != '354'):
            raise RuntimeError('Error sending DATA command')
        
        client.sendall(mail_content)
            
        msg = '\r\n.\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)
        
        msg = 'QUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)