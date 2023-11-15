import socket
import Email
# import base64
import json
import re

def SendMail():
    config_file = 'config.json'
    config : dict
    HOST : str
    PORT : int
    usermail : str

    with open(config_file, 'r') as fi:
        config = json.load(fi)
        HOST = config['General']['MailServer']
        PORT = config['General']['SMTP']
        usermail = config['General']['usermail']

    email = Email.Email()
    
    #input Email content
    email.Input()
    
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
        if (email.To != b''):
            recipentList += re.split(b',|, | ', email.To)
        if (email.Cc != b''):
            recipentList += re.split(b',|, | ', email.Cc)
        if (email.Bcc != b''):
            recipentList += re.split(b',|, | ', email.Bcc)
            
        for rcpt in list(set(recipentList)):
            if (rcpt != b''):
                msg = b'RCPT TO:<' + rcpt + b'>\r\n'
                client.sendall(msg)
                response = client.recv(1024).decode('utf-8')
                if (response[:3] != '250'):
                    raise RuntimeError('Error sending RCPT')
        
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        client.recv(1024)
        
        msg = email.As_Byte()
        client.sendall(msg)
        
        msg = '\r\n.\r\nQUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)
