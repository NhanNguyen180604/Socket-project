import tkinter as tk
import os
import mimetypes
import base64
import json
import re
import socket

import Email
LINE_LENGTH = 76

def SendMail():
    def Send():
        #get to, cc, bcc, subject
        email.To = ent_to.get().encode('utf-8')
        email.Cc = ent_cc.get().encode('utf-8')
        email.Bcc = ent_bcc.get().encode('utf-8')
        email.Subject = ent_subject.get().encode('utf-8')
        
        #get content
        content = txt_content.get('1.0', tk.END)
        email.MIME_Parts.append(Email.MyMIME())
        email.MIME_Parts[0].create_body_headers()
        
        for line in content.split('\n'):
            if (line != ''):
                email.MIME_Parts[0].Content += line[:LINE_LENGTH].encode('utf-8')
                email.MIME_Parts[0].Content += '\r\n'.encode('utf-8')
        
        #get attachment
        for input_path in ent_attachment.get().split(', '):
            if (os.path.exists(input_path) and os.path.isfile(input_path) and (os.path.getsize(input_path) <= 3e+6)):
                mime_type = mimetypes.guess_type(input_path, strict=True)
                file_name = os.path.basename(input_path)
                
                with open(input_path, 'rb') as fi:
                        data = fi.read()
                        data = base64.b64encode(data)
                        attachment = Email.MyMIME()
                        attachment.create_attachment_headers(mime_type[0], file_name)
                        attachment.Content = data
                        attachment.Content += b'\r\n'
                        email.MIME_Parts.append(attachment)
                    
        #send through socket    
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
            
            msg = email.As_Byte()
            client.sendall(msg)
            
            msg = '\r\n.\r\nQUIT\r\n'
            client.sendall(msg.encode('utf-8'))
            
            client.recv(1024)
            
            send_window.quit()
    
    email = Email.Email()
    send_window = tk.Tk()
    send_window.title('Send mail')
    
    frame1 = tk.Frame(master=send_window)
    frame2 = tk.Frame(master=send_window)
    frame3 = tk.Frame(master=send_window)
    frame4 = tk.Frame(master=send_window)
    content_frame = tk.Frame(master=send_window)
    attachment_frame = tk.Frame(master=send_window)
    bton_send = tk.Button(master=send_window, command=Send, text='SEND', font=('Times New Roman', 16, 'normal'))
    
    lbl_to = tk.Label(master=frame1, text='To', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')
    lbl_cc = tk.Label(master=frame2, text='Cc', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')
    lbl_bcc = tk.Label(master=frame3, text='Bcc', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')
    lbl_subject = tk.Label(master=frame4, text='Subject', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')
    lbl_content = tk.Label(master=content_frame, text='Content', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')
    lbl_attachment = tk.Label(master=attachment_frame, text='Attachment', font=('Times New Roman', 16, 'normal'), width=10, anchor='w')

    ent_to = tk.Entry(master=frame1, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH)
    ent_cc = tk.Entry(master=frame2, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH)
    ent_bcc = tk.Entry(master=frame3, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH)
    ent_subject = tk.Entry(master=frame4, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH)
    txt_content = tk.Text(master=content_frame, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH, height=20)
    ent_attachment = tk.Entry(master=attachment_frame, font=('Times New Roman', 16, 'normal'), width=LINE_LENGTH)
    
    lbl_to.pack(side=tk.LEFT)
    ent_to.pack(side=tk.RIGHT)
    lbl_cc.pack(side=tk.LEFT)
    ent_cc.pack(side=tk.RIGHT)
    lbl_bcc.pack(side=tk.LEFT)
    ent_bcc.pack(side=tk.RIGHT)
    lbl_subject.pack(side=tk.LEFT)
    ent_subject.pack(side=tk.RIGHT)
    lbl_content.pack(side=tk.LEFT)
    txt_content.pack(side=tk.RIGHT)
    lbl_attachment.pack(side=tk.LEFT)
    ent_attachment.pack(side=tk.RIGHT)
    
    frame1.pack()
    frame2.pack()
    frame3.pack()
    frame4.pack()
    content_frame.pack()
    attachment_frame.pack()
    bton_send.pack(side=tk.RIGHT)
    
    

menu = tk.Tk()
menu.title('Fake Chinese mail client app')

btn_sendmail = tk.Button(master=menu, text='Send mail', width=12, font=('Times New Roman', 36, 'bold'), command=SendMail)
btn_checkmail = tk.Button(master=menu, text='Check mail', width=12, font=('Times New Roman', 36, 'bold'))
btn_quit = tk.Button(master=menu, text='Quit', width=12, font=('Times New Roman', 36, 'bold'), command=menu.quit)

btn_sendmail.pack()
btn_checkmail.pack()
btn_quit.pack()

menu.mainloop()