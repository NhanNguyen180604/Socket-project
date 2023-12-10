import random
import string
import time
import os
import mimetypes
import base64
import json
import io

MIME_VERSION = 'MIME-Version: 1.0'
BUFFER_SIZE = 10000

class MyMIME:
    def __init__(self):
        self.Headers = b''
        self.Content = b''
    
    def create_body_headers(self):
        Content_type = f'Content-Type: text/plain'
        charset = 'charset="utf-8"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: base64'
        self.Headers = (f'{Content_type}; {charset}\r\n{Content_transfer_encoding}\r\n').encode('utf-8')
        
    def create_attachment_headers(self, mime_type : str, file_name : str):
        Content_type = f'Content-Type: {mime_type}; name="{file_name}"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: base64'
        Content_disposition = 'Content-Disposition: attachment'
        self.Headers = (f'{Content_type}\r\n{Content_transfer_encoding}\r\n{Content_disposition}; filename="{file_name}"\r\n').encode('utf-8')
    
class Email:
    def __init__(self):
        self.From = b''
        self.To = b''
        self.Cc = b''
        self.Bcc = b''
        self.Subject = b''
        self.Boundary = b''
        self.Date = ''
        self.MIME_Parts = []
            
    def Input_By_String(self, To: str, Cc: str, Bcc: str, Subject: str, body: str, files_paths: list):
        with open('config.json', 'r') as config_file:
            config = json.load(config_file)
            username = config['Account']['username']
            usermail = config['Account']['usermail']
            FORMAT = config['General']['FORMAT']
        
        username = username.encode(FORMAT)
        username = base64.b64encode(username).decode(FORMAT)
        username = f'=?UTF-8?B?{username}?='
        
        self.Date = time.ctime(time.time())
        self.From = f'{username} <{usermail}>'.encode(FORMAT)
        self.To = To.encode(FORMAT)
        self.Cc = Cc.encode(FORMAT)
        self.Bcc = Bcc.encode(FORMAT)   
        Subject = Subject.encode(FORMAT)
        Subject = base64.b64encode(Subject).decode(FORMAT)
        self.Subject = f'=?UTF-8?B?{Subject}?='.encode(FORMAT)
        
        self.MIME_Parts.append(MyMIME())
        self.MIME_Parts[0].create_body_headers()
        
        body_writer = io.BytesIO()
        for line in body.splitlines():
            line = f'{line[:BUFFER_SIZE]}\n'.encode('utf-8')
            line = base64.b64encode(line) + b'\r\n'
            body_writer.write(line)
        self.MIME_Parts[0].Content = body_writer.getvalue()
        
        for path in files_paths:             
            mime_type = mimetypes.guess_type(path, strict=True)
            file_name = os.path.basename(path)
            
            with open(path, 'rb') as fi:
                data = fi.read()
                data = base64.b64encode(data)
                attachment = MyMIME()
                attachment.create_attachment_headers(mime_type[0], file_name)
                attachment.Content = data
                self.MIME_Parts.append(attachment)
    
    def As_Byte(self) -> bytes:     
        result = io.BytesIO()
        
        if (len(self.MIME_Parts) > 1):
            if (self.Boundary == b''):
                self.Boundary = generate_boundary()
            result.write(b'Content-Type: multipart/mixed; boundary="' + self.Boundary + b'"\r\n')
            
        #header parts
        result.write((f'Date: {self.Date}\r\n').encode('utf-8'))
        
        result.write(b'From: ' + self.From + b'\r\n')
        
        if (self.To != b''):
            result.write(b'To: ' + self.To + b'\r\n')
        
        if (self.Cc != b''):
            result.write(b'Cc: ' + self.Cc + b'\r\n')
            
        result.write(b'Subject: ' + self.Subject + b'\r\n')
        
        result.write((MIME_VERSION + '\r\n').encode('utf-8'))
        
        #body parts
        if (len(self.MIME_Parts) == 1):
            result.write(self.MIME_Parts[0].Headers + b'\r\n')
            result.write(self.MIME_Parts[0].Content + b'\r\n')
        else:         
            result.write(b'\r\n--' + self.Boundary + b'\r\n')
            result.write(self.MIME_Parts[0].Headers + b'\r\n')
            result.write(self.MIME_Parts[0].Content + b'\r\n')
            
            for attachment in self.MIME_Parts[1:]:
                result.write(b'--' + self.Boundary + b'\r\n')
                result.write(attachment.Headers + b'\r\n')
                data = attachment.Content
                
                start = 0
                while (start < len(data)):
                    result.write(data[start : start + BUFFER_SIZE] + b'\r\n')
                    start += BUFFER_SIZE
                
            result.write(b'--' + self.Boundary + b'--\r\n')
        
        return result.getvalue()
    
def generate_boundary() -> bytes:
    characters = string.ascii_letters + string.digits
    boundary = ''.join(random.choice(characters) for i in range(36))
    return boundary.encode('utf-8')