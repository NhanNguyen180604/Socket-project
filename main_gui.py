import customtkinter as ctk
from tkinter import filedialog
import mysql.connector
import os
import Email
import clientSMTP
import clientPOP3
import threading
import json
import time

ctk.set_appearance_mode('dark')
ctk.set_default_color_theme('blue')

class App(ctk.CTk):
    def __init__(self, width, height):
        super().__init__()
        self.title('Fake mail client app')
        self.geometry(f'{width}x{height}+{int((self.winfo_screenwidth() - width) / 2)}+{int((self.winfo_screenheight() - height) / 2)}')
        self.minsize(800, 600)
        
        self.mail_content_frame = MailContentFrame(self)
        self.mail_list_frame = MailListFrame(self, self.mail_content_frame)
        self.folder_frame = MenuFrame(self, self.mail_list_frame)
        
        self.mainloop()

class MailContentFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(corner_radius=0)
        self.label = ctk.CTkLabel(self, fg_color='yellow')
        self.label.pack(expand=True, fill='both', padx=30, pady=30)
        self.place(relx=0.5, y=0, relwidth=0.5, relheight=1)
        
        # display frame
        self.display_frame = ctk.CTkFrame(self)
        
    def display_mail(self, uidl, folder):
        pass

class MailListFrame(ctk.CTkFrame):
    def __init__(self, master, mail_content_frame: MailContentFrame):
        super().__init__(master)
        self.configure(corner_radius=0)
        self.place(relx=0.2, y=0, relwidth=0.3, relheight=1)   
        
        # top label
        self.top_frame = ctk.CTkFrame(self)
        self.top_frame.pack(side='top', fill='x', padx=5, pady=5)
        
        self.stringVar = ctk.StringVar()
        self.label = ctk.CTkLabel(self.top_frame, textvariable=self.stringVar, 
                                  font=('Calibri', 18, 'bold'), justify='left',
                                  corner_radius=10)
        self.label.pack(side='top', fill='x', padx=5, pady=5)
        
        # mail list frame
        self.mail_list_frame = ctk.CTkScrollableFrame(self, corner_radius=10)
        self.mail_list_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        self.mail_frame_list = []
        self.set_mail_list('Inbox')
        
        # link to mail_content_frame
        self.mail_content_frame = mail_content_frame
                
    def set_mail_list(self, folder_name):    
        for mail_button in self.mail_frame_list:
            mail_button.destroy()
        self.mail_frame_list = []
        
        mail_list = get_mail_list(folder_name)
            
        n = len(mail_list)
        self.stringVar.set(f'{folder_name} {n} Messages')
        
        for mail in reversed(mail_list):
            mail_frame = self.create_mail_frame(mail, folder_name)
            self.mail_frame_list.append(mail_frame)
            mail_frame.pack(side='top', fill='x', expand=True)
        
    def create_mail_frame(self, mail, folder):
        uidl = mail[0]
        From = mail[1]
        Subject = mail[2]
        IsRead = mail[3]
        
        # create widgets
        mail_frame = ctk.CTkFrame(self.mail_list_frame, corner_radius=0, fg_color='transparent')
        from_label = ctk.CTkLabel(mail_frame, text=From, font=('Calibri', 14), anchor='w', fg_color='transparent')
        subject_label = ctk.CTkLabel(mail_frame, text=Subject, font=('Calibri', 14), anchor='w', fg_color='transparent')
        
        # style read or unread
        if IsRead == False:
            from_label.configure(font=('Calibri', 16, 'bold'))
            subject_label.configure(font=('Calibri', 16, 'bold'))
        else:
            from_label.configure(font=('Calibri', 14))
            subject_label.configure(font=('Calibri', 14))
            
        from_label.configure(text_color='white')
        subject_label.configure(text_color='white')

        # pack
        from_label.pack(side='top', expand=True, fill='x', padx=5)
        subject_label.pack(side='top', expand=True, fill='x', padx=5)
    
        # left mouse click event
        mail_frame.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder))
        from_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder))
        subject_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder))
        
        # mouse hover event
        mail_frame.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        from_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        subject_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        
        # mouse stop hovering event
        mail_frame.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        from_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        subject_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        
        return mail_frame
    
    def mail_click(self, uidl, folder):
        self.mail_content_frame.display_mail(uidl, folder)
        
    def mail_hover(self, mail):
        for i in mail:
            i.configure(fg_color='#12131a')
            
    def mail_stop_hovering(self, mail):
        for i in mail:
            i.configure(fg_color='transparent')
        
class MailSendingWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master)
        self.geometry('800x600')
        self.title('Sending mail')
        self.minsize(width=600, height=400)

        # to widgets
        self.to_label = ctk.CTkLabel(self, text='To', font=('Calibri', 16, 'bold'), anchor='w')
        self.to_entry = ctk.CTkEntry(self, font=('Calibri', 16), fg_color='#333333')
        self.to_label.place(relx=0.05, rely=0.02, relwidth=0.05, relheight=0.07, anchor='nw')
        self.to_entry.place(relx=0.15, rely=0.02, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # cc widgets
        self.cc_label = ctk.CTkLabel(self, text='Cc', font=('Calibri', 16, 'bold'), anchor='w')
        self.cc_entry = ctk.CTkEntry(self, font=('Calibri', 16), fg_color='#333333')
        self.cc_label.place(relx=0.05, rely=0.1, relwidth=0.05, relheight=0.07, anchor='nw')
        self.cc_entry.place(relx=0.15, rely=0.1, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # bcc widgets
        self.bcc_label = ctk.CTkLabel(self, text='Bcc', font=('Calibri', 16, 'bold'), anchor='w')
        self.bcc_entry = ctk.CTkEntry(self, font=('Calibri', 16), fg_color='#333333')
        self.bcc_label.place(relx=0.05, rely=0.18, relwidth=0.05, relheight=0.07, anchor='nw')
        self.bcc_entry.place(relx=0.15, rely=0.18, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # subject widgets
        self.subject_label = ctk.CTkLabel(self, text='Subject', font=('Calibri', 16, 'bold'), anchor='w')
        self.subject_entry = ctk.CTkEntry(self, font=('Calibri', 16), fg_color='#333333')
        self.subject_label.place(relx=0.05, rely=0.26, relwidth=0.1, relheight=0.07, anchor='nw')
        self.subject_entry.place(relx=0.15, rely=0.26, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # content textbox
        self.textbox = ctk.CTkTextbox(self, font=('Calibri', 16), fg_color='#333333')
        self.textbox.insert('0.0', 'Type your body here')
        self.textbox.place(relx=0.5, rely=0.34, relwidth=0.9, relheight=0.5, anchor='n')
        
        # attachment button
        self.files_paths = []
        self.att_button = ctk.CTkButton(self, text='Attach files', font=('Calibri', 16, 'bold'), corner_radius=20, 
                                        command=self.get_files_paths)
        self.att_button.place(relx=0.95, rely=0.9, relheight=0.07, anchor='ne')
        
        # send button
        self.send_button = ctk.CTkButton(self, text='Send', font=('Calibri', 16, 'bold'), corner_radius=20, 
                                         command=self.send_mail)
        self.send_button.place(relx=0.05, rely=0.9, relheight=0.07, anchor='nw')
        
    def get_files_paths(self):
        self.files_paths += filedialog.askopenfilenames()
        self.files_paths = [path for path in self.files_paths if (os.path.getsize(path) <= 3e+6)]
        
    def send_mail(self):
        To = self.to_entry.get()
        Cc = self.cc_entry.get()
        Bcc = self.bcc_entry.get()   
        Subject = self.subject_entry.get()[:100]
        body = self.textbox.get('0.0', 'end')
        body = body.replace('\n\n', '\n \n')
        body = body.replace('\n', '\r\n').encode('utf-8')
        
        email = Email.Email()
        email.Input_By_String(To, Cc, Bcc, Subject, body, self.files_paths)
        clientSMTP.send_mail(email)
        self.destroy()
    
class MenuFrame(ctk.CTkFrame):
    def __init__(self, master, mail_list_frame: MailListFrame):
        super().__init__(master)
        self.configure(corner_radius=0)
        self.place(x=0, y=0, relwidth=0.2, relheight=1)
        self.mail_sending_window = None
        self.add_widgets()
        # self.configure(fg_color='#13161a')
        self.mail_list_frame = mail_list_frame
        
    def add_widgets(self):
        new_message_button = ctk.CTkButton(self, text='Compose', font=('Calibri', 18, 'bold'),
                                           corner_radius=20, command=self.create_send_mail_window)
        new_message_button.place(relx=0.5, rely=0.03, relwidth=0.8, relheight=0.07, anchor='n')
        
        mail_folders_label =ctk.CTkLabel(self, text='Mail folders', font=('Calibri', 16, 'bold'))
        mail_folders_label.place(relx=0.5, rely = 0.15, relwidth=0.7, relheight=0.05, anchor='n')
        
        #folder buttons
        inbox_button = ctk.CTkButton(self, text='Inbox', 
                                     fg_color='transparent', hover_color='#12131a', 
                                     command=lambda: self.mail_list_frame.set_mail_list('Inbox'))
        important_button = ctk.CTkButton(self, text='Important', 
                                         fg_color='transparent', hover_color='#12131a', 
                                         command=lambda: self.mail_list_frame.set_mail_list('Important'))
        college_button = ctk.CTkButton(self, text='College', 
                                         fg_color='transparent', hover_color='#12131a', 
                                         command=lambda: self.mail_list_frame.set_mail_list('College'))
        spam_button = ctk.CTkButton(self, text='Spam', 
                                         fg_color='transparent', hover_color='#12131a', 
                                         command=lambda: self.mail_list_frame.set_mail_list('Spam'))
        # sent_button = ctk.CTkButton(self, text='Sent',
        #                             fg_color='transparent', hover_color='#12131a', 
        #                             command=lambda: self.mail_list_frame.set_mail_list('Sent'))
        
        inbox_button.place(relx=0.5, rely=0.2, relwidth=0.6, relheight=0.05, anchor='n')
        important_button.place(relx=0.5, rely=0.25, relwidth=0.6, relheight=0.05, anchor='n')
        college_button.place(relx=0.5, rely=0.3, relwidth=0.6, relheight=0.05, anchor='n')
        spam_button.place(relx=0.5, rely=0.35, relwidth=0.6, relheight=0.05, anchor='n')
        # sent_button.place(relx=0.5, rely=0.4, relwidth=0.6, relheight=0.05, anchor='n')
        
    def create_send_mail_window(self):
        if self.mail_sending_window is None or not self.mail_sending_window.winfo_exists():
            self.mail_sending_window = MailSendingWindow(self)
        else:
            self.mail_sending_window.focus()
    
def get_mail_list(folder_name):
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASSWORD')
    with mysql.connector.connect(host='127.0.0.1', user=db_user, password=db_pass, database='mydb') as db:
        my_cursor = db.cursor()
        my_cursor.execute(f'SELECT UIDL, SenderMail, Subject, IsRead FROM email WHERE Folder = "{folder_name}"')
        mail_list = my_cursor.fetchall()
    return mail_list

def get_sent_list():
    db_user = os.environ.get('DB_USER')
    db_pass = os.environ.get('DB_PASSWORD')
    with mysql.connector.connect(host='127.0.0.1', user=db_user, password=db_pass, database='mydb') as db:
        my_cursor = db.cursor()
        my_cursor.execute(f'SELECT UIDL, SUBJECT FROM sent')
        mail_list = my_cursor.fetchall()
    return mail_list
        
def auto_load():
    with open('config.json', 'r') as fin:
        config = json.load(fin)
        interval = config['General']['Autoload']
    
    while True:
        get_message_thread = threading.Thread(target=clientPOP3.GetMessage)
        get_message_thread.start()
        get_message_thread.join()
        time.sleep(interval)
            
def main():
    auto_load_thread = threading.Thread(target=auto_load, daemon=True)
    auto_load_thread.start()
    App(1200, 600)

if __name__ == '__main__':
    main()