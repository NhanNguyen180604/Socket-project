import random
import string
import time

class MyMIME:
    Headers = ''
    Content = ''
    
    def TextBody(self):
        Content_type = f'Content-Type: text/plain'
        charset = 'charset = "utf-8"'
        Content_transfer_encoding = 'Content-Transfer-Encoding: 8bit'
        self.Headers = f'{Content_type}; {charset}\r\n{Content_transfer_encoding}\r\n'
        
    def CreateHeader(self, mime_type : str, file_name : str):
        Content_type = f'Content-Type: {mime_type}'
        Content_transfer_encoding = 'Content-Transfer-Encoding: base64'
        Content_disposition = 'Content-Disposition: attachment'
        self.Headers = f'{Content_type}\r\n{Content_transfer_encoding}\r\n{Content_disposition}; filename="{file_name}"\r\nMIME-Version: 1.0\r\n'
        
    def As_String(self) -> str :
        return f'{self.Headers}\r\n{self.Content}\r\n'
    
class Email:
    MIME_Version = 'MIME-Version: 1.0'
    Subject = ''
    To = ''
    Cc = ''
    Bcc = ''
    MIME_Parts = []
    
    def As_String(self, sender_mail: str, sender_name: str) -> str:
        result = ''
        if (len(self.MIME_Parts) > 1):
            self.Boundary = GenerateBoundary()
            result = f'Content-Type: multipart/mixed; boundary="{self.Boundary}"\r\n'
        
        #header parts
        current_time = time.time()
        current_date = time.ctime(current_time)
        result += f'Date: {current_date}\r\n'
        
        result += f'From: {sender_name} <{sender_name}>\r\n'
        
        if (self.To != ''):
            result += f'To: {self.To}\r\n'
        
        if (self.Cc != ''):
            result += f'Cc: {self.Cc}\r\n'
            
        result += f'Subject: {self.Subject}\r\n\r\n'
        
        #body
        if (len(self.MIME_Parts) == 1):
            result += self.MIME_Parts[0].Content
        else:
            result += 'This is a multi-part message in MIME format.\r\n'
            for i in self.MIME_Parts:
                result += self.Boundary + '\r\n'
                result += i.As_String()
            result += self.Boundary + '--\r\n'
        
        result += '\r\n.\r\nQUIT\r\n'
        return result
    
def GenerateBoundary() -> str:
    characters = string.ascii_letters + string.digits
    boundary = ''.join(random.choice(characters) for i in range(36))
    return f'--{boundary}'