import socket
import Email
import re
import base64

def SendMail():
    HOST = '127.0.0.1'
    PORT = 9696
    
    usermail = 'ntnhan@gmail.com'
    username = "Nguyễn Thành Nhân"
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
        
        print('================Sending================')
        client.sendall(email.As_String(sender_mail=usermail, sender_name=username).encode('utf-8'))
        print('===========Finished sending============')
        
        client.recv(1024)