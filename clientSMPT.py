import socket
import Email
import base64
import json

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
            
        msg = 'EHLO [127.0.0.1]\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = f'MAIL FROM:<{usermail}>\r\n'
        client.sendall(msg.encode('utf-8'))
        
        recipentList = []
        if (email.To != ''):
            recipentList += email.To.split(', ')
        if (email.Cc != ''):
            recipentList += email.Cc.split(', ')
        if (email.Bcc != ''):
            recipentList += email.Bcc.split(', ')
            
        for rcpt in list(set(recipentList)):
            msg = f'RCPT TO:<{rcpt}>\r\n'
            client.sendall(msg.encode('utf-8'))
            if (client.recv(1024).decode('utf-8')[:3] != '250'):
                raise RuntimeError('250 reply not received from server when sending RCPT')
        
        #send mail content
        print('================Sending================')
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.sendall(email.As_String(sender_mail=usermail, sender_name=username).encode('utf-8'))
        
        msg = '\r\n.\r\nQUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)
        print('===========Finished sending============')