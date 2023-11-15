import socket
import Email
import base64
import json
import re

def SendMail():
    config_file = 'config.json'
    config : dict
    HOST : str
    PORT : int
    usermail : str
    username : str

    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        PORT = config['General']['SMTP']
        usermail = config['General']['usermail']
        username = config['General']['username']
    
    username = username.encode('utf-8')
    username = base64.b64encode(username).decode('utf-8')
    username = f'=?UTF-8?B?{username}?='

    email = Email.Email()
    
    #input Email content
    email.Input()
            
    # li = email.As_List(sender_mail=usermail, sender_name=username)
    
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
        
        msg = f'MAIL FROM:<{usermail}>\r\n'
        client.sendall(msg.encode('utf-8'))
        
        recipentList = []
        if (email.To != ''):
            recipentList += re.split(',|, | ', email.To)
        if (email.Cc != ''):
            recipentList += re.split(',|, | ', email.Cc)
        if (email.Bcc != ''):
            recipentList += re.split(',|, | ', email.Bcc)
            
        for rcpt in list(set(recipentList)):
            msg = f'RCPT TO:<{rcpt}>\r\n'
            client.sendall(msg.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            if (response[:3] != '250'):
                raise RuntimeError('Error sending RCPT')
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)
        
        msg = email.As_String(sender_mail=usermail, sender_name=username)
        client.sendall(msg.encode('utf-8'))
        
        msg = '\r\n.\r\nQUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)