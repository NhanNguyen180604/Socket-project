import socket
import time
# import sys

def SendMail():
    HOST = '127.0.0.1'
    PORT = 9696
    
    user = 'ntnhan@gmail.com'
    rcpt = ['ntnhan@gmail.com']
    
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client:
        #initialize TCP connection
        client.connect((HOST, PORT))
        response = client.recv(1024).decode('utf-8')
        
        if (response[:3] != '220'):
            print('220 not received from server!')
            return
        
        count = 0
        while True:
            match count:
                case 0:
                    msg = 'EHLO [127.0.0.1]\r\n'
                case 1:
                    msg = 'MAIL FROM:<' + user + '>\r\n'
                case 2:
                    for receiver in rcpt:
                        msg = 'RCPT TO:<' + receiver + '>\r\n'
                        client.sendall(msg.encode('utf-8'))
                        response = client.recv(1024).decode('utf-8')
                        if (response[:3] != '250'):
                            print('Error occurred while trying to send RCPT info!')
                            return
                    break
                
            client.sendall(msg.encode('utf-8'))
            response = client.recv(1024).decode('utf-8')
            if (response[:3] != '250'):
                print('An error has occurred')
                return
            
            count += 1
            
        #send mail content
        msg = 'DATA\r\n'
        client.sendall(msg.encode('utf-8'))
        response = client.recv(1024).decode('utf-8')
        if (response[:3] != '354'):
            print('354 response not received from the server!')
            return
        
        current_time = time.time()
        current_date = time.ctime(current_time)
        
        msg = 'Date: ' + current_date + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'To: ' + rcpt[0] + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'Cc: ' + rcpt[0] + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'From: ' + user + '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'Subject: testing 7\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = '\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = 'pls work\r\n'
        client.sendall(msg.encode('utf-8'))
        
        msg = '\r\n.\r\n'  #the end of mail content
        client.sendall(msg.encode('utf-8'))
        
        msg = 'QUIT\r\n'
        client.sendall(msg.encode('utf-8'))