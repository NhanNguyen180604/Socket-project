import socket
import Email
import os
import json
import re
import time
import mysql.connector
import clientPOP3

def send_mail_util():
    email = Email.Email()
    
    #input Email content
    email.Input()
    send_mail(email)

def send_mail(email: Email.Email):
    mail_content = email.As_Byte()    
    config_file = 'SocketProgramming/config.json'

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
            
        msg = '\r\n.\r\nQUIT\r\n'
        client.sendall(msg.encode('utf-8'))
        
        client.recv(1024)
        save_as_sent(mail_content)
        
def save_as_sent(email: bytes):
    email = email.decode('utf-8')
    now = time.localtime(time.time())
    
    sent_id = '{:0>4}{:0>2}{:0>2}{:0>2}{:0>2}{:0>2}'.format(now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
    file_name = sent_id + '.msg'

    filecontent, From, subject, content = clientPOP3.string_parser(email)
    subject = subject.split(' ', maxsplit=1)[1]
    filepath = os.path.join(os.getcwd(), 'Sent', file_name)             
    
    os.makedirs(os.path.dirname(filepath),exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as fi:
        fi.write(filecontent)
    
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASSWORD')
    with open(os.path.join(os.getcwd(), 'SocketProgramming/config.json'), 'r') as config_file:
        config = json.load(config_file)
        db_name = config['General']['Database']
        
    with mysql.connector.connect(host='127.0.0.1', user=db_user, password=db_pass, database=db_name) as db:
        my_cursor = db.cursor()
        command = 'INSERT INTO sent VALUES (%s, %s)'
        val = (sent_id, subject)
        my_cursor.execute(command, val)
        db.commit()