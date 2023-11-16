import random
import string
import time
import os
import mimetypes
import base64
import re
import json
import math
import multiprocessing

LINE_LENGTH = 76
MIME_VERSION = 'MIME-Version: 1.0'

class MyMIME:
    Headers = b''
    Content = b''
    
    def create_body_headers(self):
        Content_type = f'Content-Type: text/plain'
        charset = 'charset="utf-8"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: 8bit'
        self.Headers = (f'{Content_type}; {charset}\r\n{Content_transfer_encoding}\r\n').encode('utf-8')
        
    def create_attachment_headers(self, mime_type : str, file_name : str):
        Content_type = f'Content-Type: {mime_type}; name="{file_name}"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: base64'
        Content_disposition = 'Content-Disposition: attachment'
        self.Headers = (f'{Content_type}\r\n{Content_transfer_encoding}\r\n{Content_disposition}; filename="{file_name}"\r\n').encode('utf-8')
    
    
class Email:
    Subject = b''
    To = b''
    Cc = b''
    Bcc = b''
    Boundary = b''
    MIME_Parts = []
    
    def Input(self):             
        print("Enter email's detail, press enter to skip")
        user_input = {}
        user_input['To'] = input('To: ').encode('utf-8')
        user_input['Cc'] = input('Cc: ').encode('utf-8')
        user_input['Bcc'] = input('Bcc: ').encode('utf-8')   
        user_input['Subject'] = input('Subject: ').encode('utf-8')
        
        user_input['MIME_Parts'] = []
        print(f'Body (each line should not exceed {LINE_LENGTH} letters):')
        user_input['MIME_Parts'].append(MyMIME())
        user_input['MIME_Parts'][0].create_body_headers()
        
        while True:
            line = input()
            if (line == ''):
                break
            line = line[:LINE_LENGTH] + '\r\n'
            user_input['MIME_Parts'][0].Content += line.encode('utf-8')
    
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
        self.To = fields['To']
        self.Cc = fields['Cc']
        self.Bcc = fields['Bcc']
        self.Subject = fields['Subject']
        for i in fields['MIME_Parts']:
            self.MIME_Parts.append(i)
    
    def As_Byte(self) -> bytes:
        config_file = 'config.json'
        usermail = ''
        username = ''
        
        with open(config_file, 'r') as fi:
            config = json.load(fi)
            usermail = config['General']['usermail']
            username = config['General']['username']
            
        username = username.encode('utf-8')
        username = base64.b64encode(username).decode('utf-8')
        username = f'=?UTF-8?B?{username}?='
        
        result = b''
        
        if (len(self.MIME_Parts) > 1):
            if (self.Boundary == b''):
                self.Boundary = generate_boundary()
            result += b'Content-Type: multipart/mixed; boundary="' + self.Boundary + b'"\r\n'
            
        #header parts
        current_time = time.time()
        current_date = time.ctime(current_time)
        result += (f'Date: {current_date}\r\n').encode('utf-8')
        
        result += (f'From: {username} <{usermail}>\r\n').encode('utf-8')
        
        if (self.To != ''):
            result += b'To: ' + self.To + b'\r\n'
        
        if (self.Cc != ''):
            result += b'Cc: ' + self.Cc + b'\r\n'
            
        result += b'Subject: ' + self.Subject + b'\r\n'
        
        result += (MIME_VERSION + '\r\n').encode('utf-8')
        
        #body parts
        if (len(self.MIME_Parts) == 1):
            result += self.MIME_Parts[0].Headers + b'\r\n'
            for i in re.split(b'\r\n', self.MIME_Parts[0].Content):
                if (i != b'') :
                    result += i + b'\r\n'
        else:         
            result += (b'\r\n--' + self.Boundary + b'\r\n')
            result += (self.MIME_Parts[0].Headers + b'\r\n')
            for i in re.split(b'\r\n', self.MIME_Parts[0].Content):
                result += (i + b'\r\n')
            
            for i in range(1, len(self.MIME_Parts)):
                result += (b'--' + self.Boundary + b'\r\n')
                result += (self.MIME_Parts[i].Headers + b'\r\n')
                data = self.MIME_Parts[i].Content
                
                start = 0
                data_chunk = []
                jump = math.ceil((int(len(data)) / multiprocessing.cpu_count()) / LINE_LENGTH) * LINE_LENGTH
                while (start < len(data)):
                    data_chunk.append(data[start : start + jump])
                    start += jump
                    
                with multiprocessing.Pool() as pool:
                    items = pool.map(split_into_lines, data_chunk)
                    for _ in items:
                        result += _
                
            result += (b'--' + self.Boundary + b'--\r\n')
        
        return result
    
    def As_String(self) -> str:
        config_file = 'config.json'
        usermail = ''
        username = ''
        
        with open(config_file, 'r') as fi:
            config = json.load(fi)
            usermail = config['General']['usermail']
            username = config['General']['username']
            
        username = username.encode('utf-8')
        username = base64.b64encode(username).decode('utf-8')
        username = f'=?UTF-8?B?{username}?='
        
        result = ''
        Boundary = ''
        
        if (len(self.MIME_Parts) > 1):
            if (self.Boundary == b''):
                self.Boundary = generate_boundary()
            Boundary = self.Boundary.decode('utf-8')
            result += f'Content-Type: multipart/mixed; boundary="{Boundary}"\r\n'
            
        #header parts
        current_time = time.time()
        current_date = time.ctime(current_time)
        result += (f'Date: {current_date}\r\n')
        
        result += (f'From: {username} <{usermail}>\r\n')
        
        if (self.To != ''):
            result += f'To: {self.To.decode('utf-8')}\r\n'
        
        if (self.Cc != ''):
            result += f'Cc: {self.Cc.decode('utf-8')}\r\n'
            
        result += f'Subject: {self.Subject.decode('utf-8')}\r\n'
        
        result += (MIME_VERSION + '\r\n')
        
        #body parts
        if (len(self.MIME_Parts) == 1):
            result += self.MIME_Parts[0].Headers.decode('utf-8') + '\r\n'
            for i in re.split('\r\n', self.MIME_Parts[0].Content.decode('utf-8')):
                if (i != '') :
                    result += i + '\r\n'
        else:         
            result += ('\r\n' + Boundary + '\r\n')
            result += (self.MIME_Parts[0].Headers.decode('utf-8') + '\r\n')
            for i in re.split('\r\n', self.MIME_Parts[0].Content.decode('utf-8')):
                result += (i + '\r\n')
            
            for i in range(1, len(self.MIME_Parts)):
                result += ('--' + Boundary + '\r\n')
                result += (self.MIME_Parts[i].Headers.decode('utf-8') + '\r\n')
                data = self.MIME_Parts[i].Content
                start = 0
                data_chunk = []
                jump = math.ceil((int(len(data)) / multiprocessing.cpu_count()) / LINE_LENGTH) * LINE_LENGTH
                while (start < len(data)):
                    data_chunk.append(data[start : start + jump])
                    start += jump
                    
                with multiprocessing.Pool() as pool:
                    items = pool.map(split_into_lines, data_chunk)
                    for _ in items:
                        result += _.decode('utf-8')
                
            result += ('--' + Boundary + '--\r\n')
        
        return result
       
def generate_boundary() -> bytes:
    characters = string.ascii_letters + string.digits
    boundary = ''.join(random.choice(characters) for i in range(36))
    return boundary.encode('utf-8')

def split_into_lines(data: bytes):
    result = b''
    start = 0
    while (start < len(data)):
        result += data[start : start + LINE_LENGTH]
        result += b'\r\n'
        start += LINE_LENGTH
                    
    return result