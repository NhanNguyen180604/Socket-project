import random
import string
import time
import os
import mimetypes
import base64
import re

LINE_LENGTH = 76
MIME_VERSION = 'MIME-Version: 1.0'

class MyMIME:
    Headers = ''
    Content = ''
    
    def TextBody(self):
        Content_type = f'Content-Type: text/plain'
        charset = 'charset="utf-8"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: 8bit'
        self.Headers = f'{Content_type}; {charset}\r\n{Content_transfer_encoding}\r\n'
        
    def CreateAttachmentHeader(self, mime_type : str, file_name : str):
        Content_type = f'Content-Type: {mime_type}; name="{file_name}"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: base64'
        Content_disposition = 'Content-Disposition: attachment'
        self.Headers = f'{Content_type}\r\n{Content_transfer_encoding}\r\n{Content_disposition}; filename="{file_name}"\r\n{MIME_VERSION}\r\n'
    
    
class Email:
    Subject = ''
    To = ''
    Cc = ''
    Bcc = ''
    Boundary = ''
    MIME_Parts = []
    
    def Input(self): 
        print("Enter email's detail, press enter to skip")
        self.To = input('To: ') 
        self.Cc = input('Cc: ')    
        self.Bcc = input('Bcc: ')    
        self.Subject = input('Subject: ')
        
        print(f'Body (each line should not exceed {LINE_LENGTH} letters):')
        self.MIME_Parts.append(MyMIME())
        self.MIME_Parts[0].TextBody()
        
        while True:
            line = input()
            if (line == ''):
                break
            self.MIME_Parts[0].Content += line[:76]
            self.MIME_Parts[0].Content += '\r\n'
    
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
                        attachment.CreateAttachmentHeader(mime_type[0], file_name)
                        attachment.Content = str(data)[2:-1]
                        attachment.Content += '\r\n'
                        self.MIME_Parts.append(attachment)
                        
                    if (input('Do you want to attach another file (Y/N): ') != 'Y'):
                        break
                
                else:
                    print('You entered an invalid path!')
                
    def As_String(self, sender_mail: str, sender_name: str) -> str:
        result = ''
        
        #header parts
        current_time = time.time()
        current_date = time.ctime(current_time)
        result += (f'Date: {current_date}\r\n')
        
        result += (f'From: {sender_name} <{sender_mail}>\r\n')
        
        if (self.To != ''):
            result += (f'To: {self.To}\r\n')
        
        if (self.Cc != ''):
            result += (f'Cc: {self.Cc}\r\n')
            
        result += (f'Subject: {self.Subject}\r\n')
        
        result += (MIME_VERSION + '\r\n')
        
        #body parts
        if (len(self.MIME_Parts) == 1):
            result += (self.MIME_Parts[0].Headers + '\r\n')
            for i in re.split('\r\n',self.MIME_Parts[0].Content):
                if (i != '') :
                    result += (i + '\r\n')
        else:         
            self.Boundary = GenerateBoundary()
            result += (f'Content-Type: multipart/mixed; boundary="{self.Boundary}"\r\n')
            
            result += ('\r\n--' + self.Boundary + '\r\n')
            result += (self.MIME_Parts[0].Headers + '\r\n')
            for i in re.split('\r\n',self.MIME_Parts[0].Content):
                result += (i + '\r\n')
            
            for i in range(1, len(self.MIME_Parts)):
                result += ('--' + self.Boundary + '\r\n')
                result += (self.MIME_Parts[i].Headers + '\r\n')
                data = self.MIME_Parts[i].Content
                while (len(data) > 0):
                    result += (data[:LINE_LENGTH] + '\r\n')
                    data = data[LINE_LENGTH:]
                
            result += ('--' + self.Boundary + '--\r\n')
        
        result += ('\r\n.\r\nQUIT\r\n')
        return result
       
def GenerateBoundary() -> str:
    characters = string.ascii_letters + string.digits
    boundary = ''.join(random.choice(characters) for i in range(36))
    return boundary