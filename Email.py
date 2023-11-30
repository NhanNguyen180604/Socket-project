import random
import string
import time
import os
import mimetypes
import base64
import re
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
        
    def Input(self):             
        with open('config.json', 'r') as fi:
            config = json.load(fi)
            usermail = config['Account']['usermail']
            username = config['Account']['username']
            
        username = username.encode('utf-8')
        username = base64.b64encode(username).decode('utf-8')
        username = f'=?UTF-8?B?{username}?='
        
        print("Enter email's detail, press enter to skip")
        user_input = {}
        user_input['Date'] = time.ctime(time.time())
        user_input['From'] = f'{username} <{usermail}>'.encode('utf-8')
        user_input['To'] = input('To: ').encode('utf-8')
        user_input['Cc'] = input('Cc: ').encode('utf-8')
        user_input['Bcc'] = input('Bcc: ').encode('utf-8')   
        subject = input('Subject (max 100 letters): ')[:100].encode('utf-8')
        subject = base64.b64encode(subject).decode('utf-8')
        user_input['Subject'] = f'=?UTF-8?B?{subject}?='.encode('utf-8')
        
        user_input['MIME_Parts'] = []
        print(f'Body:')
        user_input['MIME_Parts'].append(MyMIME())
        user_input['MIME_Parts'][0].create_body_headers()
        
        while True:
            line = input()
            if (line == ''):
                break
            line = line[:BUFFER_SIZE] + '\n'
            user_input['MIME_Parts'][0].Content += base64.b64encode(line.encode('utf-8')) + b'\r\n'
    
        if (input('Do you want to send attachment (Y/N): ') == 'Y'):
            while True:
                input_path = input('Enter path: ')
                if (os.path.exists(input_path) and os.path.isfile(input_path)):
                    if (os.path.getsize(input_path) > 3e+6):
                        print('Your file\'s size should not exceed 3MB')
                        continue
                    
                    mime_type = mimetypes.guess_type(input_path, strict=True)
                    file_name = os.path.basename(input_path)
                    
                    with open(input_path, 'rb') as fi:
                        data = fi.read()
                        data = base64.b64encode(data)
                        attachment = MyMIME()
                        attachment.create_attachment_headers(mime_type[0], file_name)
                        attachment.Content = data
                        user_input['MIME_Parts'].append(attachment)
                        
                    if (input('Do you want to attach another file (Y/N): ') != 'Y'):
                        break
                
                else:
                    print('You entered an invalid path!')
                    
        self.Input_By_Dict(user_input)
    
    def Input_By_Dict(self, fields: dict):
        self.Date = fields['Date']
        self.From = fields['From']
        self.To = fields['To']
        self.Cc = fields['Cc']
        self.Bcc = fields['Bcc']
        self.Subject = fields['Subject']
        for i in fields['MIME_Parts']:
            self.MIME_Parts.append(i)
            
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
        for line in re.split(pattern='\n', string=body):
            line = f'{line[:BUFFER_SIZE]}\r\n'.encode('utf-8')
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
    
    # fake parser, only work for this Email class
    def parse_from_bytes(self, data: bytes):
        firstLine = data.split(sep=b'\r\n', maxsplit=1)[0]
        
        self.MIME_Parts.append(MyMIME())
        
        if (b'boundary=' not in firstLine):
            headers = data.split(b'\r\n\r\n', 1)[0]
            headers = headers.replace(b': ', b'\r\n')
            headers = headers.replace(b'; ', b'\r\n')
            headers = headers.replace(b'="', b'\r\n')
            headers = headers.split(b'\r\n')
            headers = dict(zip(headers[0::2], headers[1::2]))
            
            # get info
            self.From = headers[b'From']
            self.Date = str(headers[b'Date'])
            self.To = (headers[b'To'] if (b'To' in headers) else b'')
            self.Cc = (headers[b'Cc'] if (b'Cc' in headers) else b'')
            self.Subject = (headers[b'Subject'] if (b'Subject' in headers) else b'')
            
            # get headers
            headers = io.BytesIO()
            for line in data.split(b'\r\n', 8)[5:7]:
                headers.write(line + b'\r\n')
            self.MIME_Parts[0].Headers = headers.getvalue()
            
            # get body
            self.MIME_Parts[0].Content = data.split(b'\r\n\r\n', 1)[1][:-2]
            
        else:
            self.Boundary = firstLine.split(sep=b'"')[1]
            data_part = re.split(b'--' + self.Boundary + b'\r\n|--' + self.Boundary + b'--\r\n', data)
            
            first_headers = data_part[0].replace(b': ', b'\r\n')
            first_headers = first_headers.replace(b'; ', b'\r\n')
            first_headers = first_headers.replace(b'="', b'\r\n')
            first_headers = first_headers.split(b'\r\n')
            first_headers = dict(zip(first_headers[0::2], first_headers[1::2]))
            
            # get info
            self.From = first_headers[b'From']
            self.Date = str(first_headers[b'Date'])[2:-1]
            self.To = (first_headers[b'To'] if (b'To' in first_headers) else b'')
            self.Cc = (first_headers[b'Cc'] if (b'Cc' in first_headers) else b'')
            self.Subject = (first_headers[b'Subject'] if (b'Subject' in first_headers) else b'')

            # get body
            body = data_part[1]
            headers = io.BytesIO()
            for line in body.split(b'\r\n', 3)[0:2]:
                headers.write(line + b'\r\n')
            self.MIME_Parts[0].Headers = headers.getvalue()
                
            self.MIME_Parts[0].Content = body.split(b'\r\n\r\n', 1)[1][:-2]  # use slice to remove the last \r\n
            
            # get attachment
            for i in range(2, len(data_part) - 1):
                self.MIME_Parts.append(MyMIME())
                headers = io.BytesIO()
                for line in data_part[i].split(b'\r\n', 4)[0:3]:
                    headers.write(line + b'\r\n')
                self.MIME_Parts[i - 1].Headers = headers.getvalue()
                    
                self.MIME_Parts[i - 1].Content = data_part[i].split(b'\r\n\r\n', 1)[1]
                self.MIME_Parts[i - 1].Content = self.MIME_Parts[i - 1].Content.replace(b'\r\n', b'')
                
        return self
    
def generate_boundary() -> bytes:
    characters = string.ascii_letters + string.digits
    boundary = ''.join(random.choice(characters) for i in range(36))
    return boundary.encode('utf-8')