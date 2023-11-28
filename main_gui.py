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
from PIL import Image
import base64
import mimetypes

WINDOW_WIDTH, WINDOW_HEIGHT = 1300, 600

ctk.set_appearance_mode('light')

class App(ctk.CTk):
    def __init__(self, width, height):
        super().__init__(fg_color=('#ECF4D6', '#161A30'))
        self.title('Fake mail client app')
        self.geometry(f'{width}x{height}+{int((self.winfo_screenwidth() - width) / 2)}+{int((self.winfo_screenheight() - height) / 2)}')
        self.minsize(800, 600)
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        
        self.mail_content_frame = MailContentFrame(self)
        self.mail_list_frame = MailListFrame(self, self.mail_content_frame)
        self.folder_frame = MenuFrame(self, self.mail_list_frame)
        
        self.mainloop()
        
    def close_window(self):
        # self.delete_temp_files()
        self.destroy()
        
    def delete_temp_files(self):
        path = os.path.join(os.getcwd(), 'temp')
        for file in os.listdir(path):
            os.remove(os.path.join(path, file))

class MailContentFrame(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        self.place(relx=0.5, y=0, relwidth=0.5, relheight=1)
        
        # display frame
        self.display_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        self.display_frame.pack(expand=True, fill='both')
        
    def display_mail(self, uidl, folder):
        self.display_frame.destroy()
        self.display_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        self.display_frame.pack(expand=True, fill='both')

        folderpath = os.path.join(os.getcwd(), folder)
        mail_dict = clientPOP3.ReadFile(folderpath, uidl)[0]
        
        top_frame = ctk.CTkFrame(self.display_frame, corner_radius=0, 
                                 fg_color=('#ECF4D6', '#161A30'))
        body_frame = ctk.CTkScrollableFrame(self.display_frame, corner_radius=0, 
                                            fg_color=('#ECF4D6', '#161A30'),
                                            scrollbar_button_color=('#265073', '#31304D'),
                                            scrollbar_button_hover_color=('#2D9596', '#B6BBC4'))
        att_frame = ctk.CTkScrollableFrame(self.display_frame, corner_radius=0,
                                           fg_color=('#ECF4D6', '#161A30'),
                                           scrollbar_button_color=('#265073', '#31304D'),
                                           scrollbar_button_hover_color=('#2D9596', '#B6BBC4')) if mail_dict.get('File', '') != '' else None
        
        top_frame.place(x=0, y=0, relwidth=1, relheight=0.25)
        
        # from 
        from_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        from_frame.pack(expand=True, fill='both', padx=20)
        sender_label = ctk.CTkLabel(from_frame, text=f'From: {mail_dict['From']} <{mail_dict['MailFrom']}>', 
                                    font=('Calibri', 16), fg_color='transparent', anchor='w', justify='left',
                                    text_color=('black', '#F0ECE5'))
        sender_label.pack(expand=True, fill='x')
        
        # to
        to_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        to_frame.pack(expand=True, fill='both', padx=20)
        to_label = ctk.CTkLabel(to_frame, text=f'To: {mail_dict.get('To', '')}', anchor='w',
                                font=('Calibri', 16), fg_color='transparent', justify='left',
                                text_color=('black', '#F0ECE5'))
        to_label.pack(expand=True, fill='x')
        
        # cc
        cc_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        cc_frame.pack(expand=True, fill='both', padx=20)
        cc_label = ctk.CTkLabel(cc_frame, text=f'Cc: {mail_dict.get('Cc', '')}', anchor='w',
                                font=('Calibri', 16), fg_color='transparent', justify='left',
                                text_color=('black', '#F0ECE5'))
        cc_label.pack(expand=True, fill='x')
        
        # subject
        subject_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        subject_frame.pack(expand=True, fill='both', padx=20)
        subject_label = ctk.CTkLabel(subject_frame, text=mail_dict.get('Subject', ''), anchor='w',
                                     font=('Calibri', 18, 'bold'), fg_color='transparent', justify='left',
                                     text_color=('black', '#F0ECE5'))
        subject_label.pack(expand=True, fill='x')
        
        # body
        if att_frame is not None:
            body_frame.place(x=0, rely=0.26, relwidth=1, relheight=0.63, anchor='nw')
            att_frame.place(x=0, rely=0.9, relwidth=1, relheight=0.1, anchor='nw')
        else: 
            body_frame.place(x=0, rely=0.26, relwidth=1, relheight=0.74, anchor='nw')
            
        body_label = ctk.CTkLabel(body_frame, text=mail_dict.get('Body', ''), anchor='w',
                                  font=('Calibri', 16), fg_color='transparent', justify='left', 
                                  text_color=('black', '#F0ECE5'))
        body_label.pack(expand=True, fill='x', padx=20, pady=20)
        
        self.display_frame.configure(fg_color=('#9AD0C2', '#31304D'))
        
        if mail_dict.get('File', '') == '':
            return
        
        # attachment
        for attachment in mail_dict.get('File'):
            self.create_attachment_frame(att_frame, attachment).pack(expand=True, fill='x', padx=20, pady=5)
            
            type = mimetypes.guess_type(attachment[0])[0]
            file_type = type.split('/')[0]
            if (file_type == 'image'):
                # create temporary image file on disk
                temp_file_path = os.path.join(os.getcwd(), 'temp')
                os.makedirs(temp_file_path, exist_ok=True)
                temp_file_path = os.path.join(temp_file_path, attachment[0])
                
                if os.path.exists(temp_file_path) == False:
                    with open(temp_file_path, 'wb') as temp:
                        file_data = attachment[1].encode('utf-8')
                        temp.write(base64.b64decode(file_data))
                    
                img_label = self.create_img_label_in_body(temp_file_path, body_frame, attachment[0])
                img_label.pack(side='top', padx=20, pady=5, expand=True, fill='x')
    
    def create_attachment_frame(self, att_frame, attachment: tuple):
        # attachment frame
        att_holder = ctk.CTkFrame(att_frame, fg_color='transparent')
        
        # attachment name label
        att_label = ctk.CTkLabel(att_holder, text=attachment[0], font=('Calibri', 14), 
                                 fg_color='transparent', text_color=('black', '#F0ECE5'))
        att_label.pack(side='left')

        # download button
        download_button = ctk.CTkButton(att_holder, text='Download', font=('Calibri', 14, 'italic'), 
                                        fg_color=('#ECF4D6', '#161A30'), text_color=('black', '#F0ECE5'),
                                        hover_color=('#9AD0C2', '#31304D'),
                                        command=lambda: self.download_files(attachment))
        download_button.pack(side='right')
        return att_holder
    
    def create_img_label_in_body(self, img_path ,body_frame: ctk.CTkFrame, file_name):
        img_original = Image.open(img_path)
        img_ratio = img_original.size[0] / img_original.size[1]
        img_ctk = ctk.CTkImage(light_image=img_original, dark_image=img_original)
        img_ctk.configure(size=(WINDOW_WIDTH / 2, int(WINDOW_WIDTH/ (2 * img_ratio))))
        
        label = ctk.CTkLabel(body_frame, text=file_name, font=('Calibri', 16, 'bold'),
                             image=img_ctk, compound='bottom')
        return label
    
    def download_files(self, attachment):
        file_name = attachment[0]
        file_data = attachment[1].encode('utf-8')
        type = mimetypes.guess_type(file_name)[0]
        file_type = type.split('/')[0]
        extension = f'.{type.split('/')[1]}'
        
        path = filedialog.asksaveasfilename(initialfile=file_name, defaultextension=extension,
                                            filetypes=[(file_type, extension)])
        if not path:
            return
        
        with open(path, 'wb') as downloaded_file:
            downloaded_file.write(base64.b64decode(file_data))
    
class MailListFrame(ctk.CTkFrame):
    def __init__(self, master, mail_content_frame: MailContentFrame):
        super().__init__(master, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        self.place(relx=0.2, y=0, relwidth=0.3, relheight=1)   
        
        # top label
        self.top_frame = ctk.CTkFrame(self, fg_color='transparent')
        self.top_frame.pack(side='top', fill='x', padx=5, pady=5)
        
        self.stringVar = ctk.StringVar()
        self.label = ctk.CTkLabel(self.top_frame, textvariable=self.stringVar, 
                                  fg_color=('#9AD0C2', '#31304D'), 
                                  text_color=('#265073', '#F0ECE5'),
                                  font=('Calibri', 18, 'bold'),
                                  corner_radius=10)
        self.label.pack(side='top', expand=True, fill='both')
        
        # selected mail
        self.selected_mail = None
        self.selected_uidl = None
        self.select_folder = 'Inbox'
        
        # mail list frame
        self.mail_list_frame = ctk.CTkScrollableFrame(self, corner_radius=10,
                                                      fg_color=('#9AD0C2', '#31304D'),
                                                      scrollbar_button_color=('#265073', '#161A30'),
                                                      scrollbar_button_hover_color=('#2D9596', '#B6BBC4'))
        self.mail_list_frame.pack(side='top', fill='both', expand=True, padx=5, pady=5)
        self.mail_frame_list = []
        self.set_mail_list('Inbox')
        
        # link to mail_content_frame
        self.mail_content_frame = mail_content_frame
                
    def set_mail_list(self, folder_name):    
        if folder_name != self.select_folder:
            self.selected_mail = None
            self.selected_uidl = None
            self.select_folder = folder_name
                        
        for mail_frame in self.mail_frame_list:
            mail_frame.destroy()
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
        from_label = ctk.CTkLabel(mail_frame, text=From, font=('Calibri', 14), anchor='w', fg_color='transparent', 
                                  text_color=('black', '#F0ECE5'))
        subject_label = ctk.CTkLabel(mail_frame, text=Subject, font=('Calibri', 14), anchor='w', fg_color='transparent', 
                                     text_color=('black', '#F0ECE5'))
        
        # style read or unread
        if IsRead == False:
            from_label.configure(font=('Calibri', 16, 'bold'))
            subject_label.configure(font=('Calibri', 16, 'bold'))
        else:
            from_label.configure(font=('Calibri', 14))
            subject_label.configure(font=('Calibri', 14))

        # pack
        from_label.pack(side='top', expand=True, fill='x', padx=5)
        subject_label.pack(side='top', expand=True, fill='x', padx=5)
    
        # left mouse click event
        mail_frame.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label]))
        from_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label]))
        subject_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label]))
        
        # mouse hover event
        mail_frame.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        from_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        subject_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label])) 
        
        # mouse stop hovering event
        mail_frame.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        from_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        subject_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label])) 
        
        return mail_frame
    
    def mail_click(self, uidl, folder, mail):
        # is already selected
        if self.selected_uidl == uidl:
            return
        
        # change old selected mail color
        if (self.selected_mail is not None):
            for i in self.selected_mail:
                i.configure(fg_color='transparent')
        
        self.selected_uidl = uidl
        self.selected_mail = mail
        for i in self.selected_mail:
            i.configure(fg_color=('#2D9596', '#0c0f1c'))
        
        self.mail_content_frame.display_mail(uidl, folder)
        mail[1].configure(font=('Calibri', 14))
        mail[2].configure(font=('Calibri', 14))
        
        # mark as read
        db_user = os.environ.get('DB_USER')
        db_password = os.environ.get('DB_PASSWORD')
        with mysql.connector.connect(host='127.0.0.1', user=db_user, password=db_password, database='mydb') as db:
            my_cursor = db.cursor()
            my_cursor.execute(f'UPDATE email SET IsRead = TRUE WHERE UIDL = "{uidl}"')
            db.commit()

    def mail_hover(self, mail):
        color = ('#238182', '#0c0f1c') if self.selected_mail == mail else ('#2D9596', '#161A30')
        for i in mail:
            i.configure(fg_color=color)
            
    def mail_stop_hovering(self, mail):
        color = ('#238182', '#0c0f1c') if self.selected_mail == mail else 'transparent'
        for i in mail:
            i.configure(fg_color=color)
        
class MailSendingWindow(ctk.CTkToplevel):
    def __init__(self, master):
        super().__init__(master, fg_color=('#ECF4D6', '#161A30'))
        self.geometry('800x600')
        self.title('Sending mail')
        self.minsize(width=600, height=400)

        # to widgets
        self.to_label = ctk.CTkLabel(self, text='To', font=('Calibri', 16, 'bold'), anchor='w')
        self.to_entry = ctk.CTkEntry(self, font=('Calibri', 16), 
                                     fg_color=('#9AD0C2', '#31304D'),
                                     text_color=('black', '#F0ECE5'), 
                                     border_width=0)
        self.to_label.place(relx=0.05, rely=0.02, relwidth=0.05, relheight=0.07, anchor='nw')
        self.to_entry.place(relx=0.15, rely=0.02, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # cc widgets
        self.cc_label = ctk.CTkLabel(self, text='Cc', font=('Calibri', 16, 'bold'), anchor='w')
        self.cc_entry = ctk.CTkEntry(self, font=('Calibri', 16), 
                                     fg_color=('#9AD0C2', '#31304D'),
                                     text_color=('black', '#F0ECE5'), 
                                     border_width=0)
        self.cc_label.place(relx=0.05, rely=0.1, relwidth=0.05, relheight=0.07, anchor='nw')
        self.cc_entry.place(relx=0.15, rely=0.1, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # bcc widgets
        self.bcc_label = ctk.CTkLabel(self, text='Bcc', font=('Calibri', 16, 'bold'), anchor='w')
        self.bcc_entry = ctk.CTkEntry(self, font=('Calibri', 16), 
                                      fg_color=('#9AD0C2', '#31304D'),
                                      text_color=('black', '#F0ECE5'), 
                                      border_width=0)
        self.bcc_label.place(relx=0.05, rely=0.18, relwidth=0.05, relheight=0.07, anchor='nw')
        self.bcc_entry.place(relx=0.15, rely=0.18, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # subject widgets
        self.subject_label = ctk.CTkLabel(self, text='Subject', font=('Calibri', 16, 'bold'), anchor='w')
        self.subject_entry = ctk.CTkEntry(self, font=('Calibri', 16), 
                                          fg_color=('#9AD0C2', '#31304D'),
                                          text_color=('black', '#F0ECE5'), 
                                          border_width=0)
        self.subject_label.place(relx=0.05, rely=0.26, relwidth=0.1, relheight=0.07, anchor='nw')
        self.subject_entry.place(relx=0.15, rely=0.26, relwidth=0.8, relheight=0.07, anchor='nw')
        
        # content textbox
        self.textbox = ctk.CTkTextbox(self, font=('Calibri', 16), 
                                      fg_color=('#9AD0C2', '#31304D'),
                                      text_color=('black', '#F0ECE5'), 
                                      border_width=0)
                                     
        self.textbox.insert('0.0', 'Type your body here')
        self.textbox.place(relx=0.5, rely=0.34, relwidth=0.9, relheight=0.5, anchor='n')
        
        # attachment button
        self.files_paths = []
        self.att_button = ctk.CTkButton(self, text='Attach files', font=('Calibri', 16, 'bold'), 
                                        text_color=('black', '#F0ECE5'), corner_radius=15, 
                                        command=self.get_files_paths, border_width=4,
                                        border_color=('#9AD0C2', '#31304D'),
                                        fg_color=('#ECF4D6', '#161A30'), 
                                        hover_color=('#9AD0C2', '#31304D'))
        self.att_button.place(relx=0.95, rely=0.9, relheight=0.07, anchor='ne')
        
        # attachment display
        self.att_list_frame = ctk.CTkScrollableFrame(self, fg_color=('#ECF4D6', '#161A30'), border_width=4,
                                                     border_color=('#9AD0C2', '#31304D'),
                                                     scrollbar_button_color=('#265073', '#161A30'),
                                                     scrollbar_button_hover_color=('#2D9596', '#B6BBC4'))
        
        # send button
        self.send_button = ctk.CTkButton(self, text='Send', font=('Calibri', 16, 'bold'), 
                                         text_color=('black', '#F0ECE5'), corner_radius=15, 
                                         command=self.send_mail, border_width=4,
                                         border_color=('#9AD0C2', '#31304D'),
                                         fg_color=('#ECF4D6', '#161A30'), 
                                         hover_color=('#9AD0C2', '#31304D'))
        self.send_button.place(relx=0.05, rely=0.9, relheight=0.07, anchor='nw')
        
    def get_files_paths(self):
        new_paths = filedialog.askopenfilenames()
        new_paths = [path for path in new_paths if (os.path.getsize(path) <= 3e+6)]
        self.files_paths += new_paths
        
        if len(new_paths) == 0:
            return
        
        self.att_list_frame.place(relx=0.7, rely=0.9, relheight=0.07, relwidth=0.4, anchor='ne')
        # create attachment labels
        for path in new_paths:
            self.create_attachment_frame(path).pack(expand=True, fill='x', padx=2, pady=2)
        
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
        
    def cancel_attachment(self, path, att_frame: ctk.CTkFrame):
        self.files_paths.remove(path)
        att_frame.destroy()
        print(self.files_paths)
            
    def create_attachment_frame(self, path):
        # attachment frame
        att_frame = ctk.CTkFrame(self.att_list_frame, fg_color='transparent')
        
        # attachment name label
        file_name = os.path.basename(path)
        att_label = ctk.CTkLabel(att_frame, text=file_name, font=('Calibri', 14),
                                 fg_color='transparent',
                                 text_color=('black', '#F0ECE5'))
        att_label.pack(side='left')
        
        # cancel button
        cancel_button = ctk.CTkButton(att_frame, text='X', font=('Calibri', 16, 'bold'), width=10, 
                                      text_color=('#265073', '#F0ECE5'), 
                                      fg_color='transparent',
                                      hover_color=('#9AD0C2', '#31304D'),
                                      command=lambda: self.cancel_attachment(path, att_frame))
        cancel_button.pack(side='right')
        return att_frame
    
class MenuFrame(ctk.CTkFrame):
    def __init__(self, master, mail_list_frame: MailListFrame):
        super().__init__(master, corner_radius=0, fg_color=('#ECF4D6', '#161A30'), border_width=0)
        self.place(x=0, y=0, relwidth=0.2, relheight=1)
        self.mail_sending_window = None
        self.selected_folder_button = None
        self.mail_list_frame = mail_list_frame
        self.add_widgets()
        
    def add_widgets(self):
        new_message_button = ctk.CTkButton(self, text='Compose', font=('Calibri', 18, 'bold'),
                                           fg_color='transparent', 
                                           text_color=('#265073', '#F0ECE5'), 
                                           hover_color=('#9AD0C2', '#31304D'),
                                           border_color=('#9AD0C2', '#31304D'), border_width=3,
                                           corner_radius=20, command=self.create_send_mail_window)
        new_message_button.place(relx=0.5, rely=0.03, relwidth=0.8, relheight=0.07, anchor='n')
        
        mail_folders_label = ctk.CTkLabel(self, text='Mail folders', font=('Calibri', 16, 'bold'))
        mail_folders_label.place(relx=0.5, rely = 0.15, relwidth=0.7, relheight=0.05, anchor='n')
        
        #folder buttons
        inbox_button = ctk.CTkButton(self, text='Inbox', font=('Calibri', 14, 'bold'),
                                     text_color=('#265073', '#F0ECE5'),
                                     fg_color='transparent', 
                                     hover_color=('#9AD0C2', '#31304D'),
                                     command=lambda: self.set_mail_list('Inbox', inbox_button))
        important_button = ctk.CTkButton(self, text='Important', font=('Calibri', 14, 'bold'),
                                         text_color=('#265073', '#F0ECE5'),
                                         fg_color='transparent', 
                                         hover_color=('#9AD0C2', '#31304D'), 
                                         command=lambda: self.set_mail_list('Important', important_button))
        college_button = ctk.CTkButton(self, text='College', font=('Calibri', 14, 'bold'),
                                       text_color=('#265073', '#F0ECE5'),
                                      fg_color='transparent', 
                                      hover_color=('#9AD0C2', '#31304D'), 
                                      command=lambda: self.set_mail_list('College', college_button))
        spam_button = ctk.CTkButton(self, text='Spam', font=('Calibri', 14, 'bold'),
                                    text_color=('#265073', '#F0ECE5'),
                                    fg_color='transparent', 
                                    hover_color=('#9AD0C2', '#31304D'), 
                                    command=lambda: self.set_mail_list('Spam', spam_button))
        # sent_button = ctk.CTkButton(self, text='Sent', font=('Calibri', 14, 'bold'),
        #                             text_color=('#265073', '#F0ECE5'),
        #                             fg_color='transparent', 
        #                             hover_color=('#9AD0C2', '#31304D'), 
        #                             command=lambda: self.set_mail_list('Sent', sent_button))
        
        inbox_button.place(relx=0.5, rely=0.2, relwidth=0.6, relheight=0.05, anchor='n')
        important_button.place(relx=0.5, rely=0.26, relwidth=0.6, relheight=0.05, anchor='n')
        college_button.place(relx=0.5, rely=0.32, relwidth=0.6, relheight=0.05, anchor='n')
        spam_button.place(relx=0.5, rely=0.38, relwidth=0.6, relheight=0.05, anchor='n')
        # sent_button.place(relx=0.5, rely=0.42, relwidth=0.6, relheight=0.05, anchor='n')
        
        self.set_mail_list('Inbox', inbox_button)
    
    def set_mail_list(self, folder, button):
        if (self.selected_folder_button == button):
            return
        
        # change old folder button color
        if self.selected_folder_button is not None:
            self.selected_folder_button.configure(fg_color='transparent')
        
        # switch to new selected button
        self.selected_folder_button = button
        self.selected_folder_button.configure(fg_color=('#9AD0C2', '#31304D'))
        self.mail_list_frame.set_mail_list(folder)
        
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
    App(WINDOW_WIDTH, WINDOW_HEIGHT)

if __name__ == '__main__':
    main()