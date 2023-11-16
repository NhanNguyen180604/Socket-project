import socket
import Email
import base64
import json
import re
import time

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
        
        #=============Headers=============
        #=================================
        if (len(email.MIME_Parts) > 1):
            if (email.Boundary == b''):
                email.Boundary == Email.generate_boundary()
            client.sendall(b'Content-Type: multipart/mixed; boundary="' + email.Boundary + b'"\r\n')
        
        #============send Date============
        current_time = time.time()
        current_date = time.ctime(current_time)
        msg = (f'Date: {current_date}\r\n')
        client.sendall(msg.encode('utf-8'))
        
        #============send From============
        msg = (f'From: {username} <{usermail}>\r\n')
        client.sendall(msg.encode('utf-8'))
        
        #============send To and Cc============
        if (email.To != b''):
            client.sendall(b'To: ' + email.To + b'\r\n')
        if (email.Cc != b''):
            client.sendall(b'Cc: ' + email.Cc + b'\r\n')
        
        #============send Subject============
        client.sendall(b'Subject: ' + email.Subject + b'\r\n')
        
        client.sendall((Email.MIME_VERSION + '\r\n').encode('utf-8'))
        
        #=============Body=============
        #==============================
        if (len(email.MIME_Parts) == 1):
            client.sendall(email.MIME_Parts[0].Headers + b'\r\n')
            for i in re.split(b'\r\n', email.MIME_Parts[0].Content):
                if (i != b'') :
                    client.sendall(i + b'\r\n')
        else:
            client.sendall(b'\r\n--' + email.Boundary + b'\r\n')
            client.sendall(email.MIME_Parts[0].Headers + b'\r\n')
            
            for i in re.split(b'\r\n', email.MIME_Parts[0].Content):
                client.sendall(i + b'\r\n')
                
            for i in range(1, len(email.MIME_Parts)):
                client.sendall(b'--' + email.Boundary + b'\r\n')
                client.sendall(email.MIME_Parts[i].Headers + b'\r\n')
                start = 0
                while (start < len(email.MIME_Parts[i].Content)):
                    client.sendall(email.MIME_Parts[i].Content[start : start + Email.LINE_LENGTH])
                    client.sendall(b'\r\n')
                    start += Email.LINE_LENGTH
                
            client.sendall(b'--' + email.Boundary + b'--\r\n')
            
        msg = '\r\n.\r\nQUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)