import customtkinter as ctk
from tkinter import filedialog
import mysql.connector
import os
import re
import Email
import clientSMTP
import clientPOP3
import threading
import json
import time
from PIL import Image
import base64
import mimetypes

WINDOW_WIDTH, WINDOW_HEIGHT = 1200, 600

global config
with open(os.path.join(os.getcwd(), 'config.json'), 'r') as config_file:
    config = json.load(config_file)

ctk.set_appearance_mode('system')

class App(ctk.CTk):
    def __init__(self, width, height):
        super().__init__(fg_color=('#ECF4D6', '#161A30'))
        self.title('Fake mail client app')
        self.geometry(f'{width}x{height}+{int((self.winfo_screenwidth() - width) / 2)}+{int((self.winfo_screenheight() - height) / 2)}')
        self.minsize(800, 600)
        self.protocol('WM_DELETE_WINDOW', self.close_window)
        
        self.setting_window = SettingWindow(self)
        self.mail_content_frame = MailContentFrame(self)
        self.mail_list_frame = MailListFrame(self, self.mail_content_frame)
        self.menu_frame = MenuFrame(self, self.mail_list_frame, self.setting_window)
        
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
        sender_label.pack(expand=True, fill='both')
        
        # to
        to_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        to_frame.pack(expand=True, fill='both', padx=20)
        to_label = ctk.CTkLabel(to_frame, text=f'To: {mail_dict.get('To', '')}', anchor='w',
                                font=('Calibri', 16), fg_color='transparent', justify='left',
                                text_color=('black', '#F0ECE5'))
        to_label.pack(expand=True, fill='both')
        
        # cc
        cc_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        cc_frame.pack(expand=True, fill='both', padx=20)
        cc_label = ctk.CTkLabel(cc_frame, text=f'Cc: {mail_dict.get('Cc', '')}', anchor='w',
                                font=('Calibri', 16), fg_color='transparent', justify='left',
                                text_color=('black', '#F0ECE5'))
        cc_label.pack(expand=True, fill='both')
        
        # date
        Date = f'{uidl[6:8]}/{uidl[4:6]}/{uidl[:4]}, {uidl[8:10]}:{uidl[10:12]}:{uidl[12:14]}'
        date_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        date_frame.pack(expand=True, fill='both', padx=20)
        date_label = ctk.CTkLabel(date_frame, text=Date, anchor='w',
                                  font=('Calibri', 16), fg_color='transparent', justify='left',
                                  text_color=('black', '#F0ECE5'))
        date_label.pack(expand=True, fill='both')
        
        # subject
        subject_frame = ctk.CTkFrame(top_frame, fg_color='transparent')
        subject_frame.pack(expand=True, fill='both', padx=20)
        subject_label = ctk.CTkLabel(subject_frame, text=mail_dict.get('Subject', ''), anchor='w',
                                     font=('Calibri', 18, 'bold'), fg_color='transparent', justify='left',
                                     text_color=('black', '#F0ECE5'))
        subject_label.pack(expand=True, fill='both')
        
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
        From = 'Me' if folder == 'Sent' else mail[1]
        Subject = mail[1] if folder == 'Sent' else mail[2]
        IsRead = True if folder == 'Sent' else mail[3]
        
        # create widgets
        mail_frame = ctk.CTkFrame(self.mail_list_frame, corner_radius=5, fg_color='transparent')
        mail_frame.rowconfigure((0, 1,), weight=1, uniform='a')
        mail_frame.columnconfigure((0, 1), weight=1, uniform='a')
        
        from_label = ctk.CTkLabel(mail_frame, text=From, anchor='w', fg_color='transparent', 
                                  text_color=('black', '#F0ECE5'))
        subject_label = ctk.CTkLabel(mail_frame, text=Subject, anchor='w', fg_color='transparent', 
                                     text_color=('black', '#F0ECE5'))
        Date = f'{uidl[6:8]}/{uidl[4:6]}/{uidl[:4]}'
        date_label = ctk.CTkLabel(mail_frame, text=Date, anchor='e', fg_color='transparent',
                                  text_color=('black', '#F0ECE5'))
        
        # style read or unread
        if IsRead == False:
            from_label.configure(font=('Calibri', 16, 'bold'))
            subject_label.configure(font=('Calibri', 16, 'bold'))
            date_label.configure(font=('Calibri', 16, 'bold'))
        else:
            from_label.configure(font=('Calibri', 14))
            subject_label.configure(font=('Calibri', 14))
            date_label.configure(font=('Calibri', 14))

        # grid
        from_label.grid(row=0, column=0, sticky='nsew', padx=5)
        date_label.grid(row=0, column=1, sticky='nsew', padx=5)
        subject_label.grid(row=1, column=0, sticky='nsew', columnspan=2, padx=5)
    
        # left mouse click event
        mail_frame.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label, date_label]))
        from_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label, date_label]))
        subject_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label, date_label]))
        date_label.bind('<Button-1>', command=lambda argument: self.mail_click(uidl, folder, [mail_frame, from_label, subject_label, date_label]))
        
        # mouse hover event
        mail_frame.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label, date_label])) 
        from_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label, date_label])) 
        subject_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label, date_label])) 
        date_label.bind('<Enter>', command=lambda argument: self.mail_hover([mail_frame, from_label, subject_label, date_label]))
        
        # mouse stop hovering event
        mail_frame.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label, date_label])) 
        from_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label, date_label])) 
        subject_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label, date_label])) 
        date_label.bind('<Leave>', command=lambda argument: self.mail_stop_hovering([mail_frame, from_label, subject_label, date_label]))
        
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
        mail[3].configure(font=('Calibri', 14))
        
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
        
        email = Email.Email()
        email.Input_By_String(To, Cc, Bcc, Subject, body, self.files_paths)
        clientSMTP.send_mail(email)
        self.destroy()
        
    def cancel_attachment(self, path, att_frame: ctk.CTkFrame):
        self.files_paths.remove(path)
        att_frame.destroy()
            
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
    
class SettingWindow(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        self.is_shown = False
        # widgets
        self.selected_button = None
        self.add_widgets_util()
        
    def add_widgets_util(self):
        # categories frame
        categories_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=('#9AD0C2', '#31304D'))
        categories_frame.place(x=0, y=0, relwidth = 0.25, relheight=1) 
        
        # settings frame
        settings_frame = ctk.CTkFrame(self, corner_radius=0, fg_color=('#ECF4D6', '#161A30'))
        settings_frame.place(relx=0.25, y=0, relwidth=0.75, relheight=1)
        
        # categories and settings widgets
        entry_list = []
        self.add_widgets(categories_frame, settings_frame, entry_list)
        
        # save button
        save_button = ctk.CTkButton(categories_frame, text='Save',
                                    font=('Calibri', 16, 'bold'),
                                    text_color=('#265073', '#F0ECE5'),
                                    fg_color='transparent', 
                                    hover_color=('#ECF4D6', '#161A30'),
                                    border_color=('#ECF4D6', '#161A30'),
                                    border_width=5,
                                    corner_radius=20,
                                    command=lambda: self.save_options(entry_list))
        save_button.place(relx=0.5, rely=0.8, relwidth=0.7, relheight=0.07, anchor='s')
        
        # toggle button
        toggle_button = ctk.CTkButton(categories_frame, text='Mailbox', 
                                      font=('Calibri', 16, 'bold'),
                                      text_color=('#265073', '#F0ECE5'),
                                      fg_color='transparent', 
                                      hover_color=('#ECF4D6', '#161A30'),
                                      border_color=('#ECF4D6', '#161A30'),
                                      border_width=5,
                                      corner_radius=20,
                                      command=self.toggle)
        toggle_button.place(relx=0.5, rely=0.9, relwidth=0.7, relheight=0.07, anchor='s')
    
    def add_widgets(self, categories_frame, settings_frame, entry_list):        
        # settings widgets
        # general
        general_frame = ctk.CTkFrame(settings_frame, corner_radius=0, fg_color='transparent')
        general_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        mail_server_label = ctk.CTkLabel(general_frame, text='Mail server', font=('Calibri', 20, 'bold'), 
                                         justify='left', anchor='w')
        mail_server_label.place(relx=0.05, rely=0.1, relheight=0.1)
        mail_server_entry = ctk.CTkEntry(general_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        mail_server_entry.insert(0, string=config['General']['MailServer'])
        mail_server_entry.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.1)
        entry_list.append(mail_server_entry)
        
        SMTP_label = ctk.CTkLabel(general_frame, text='SMTP port', font=('Calibri', 20, 'bold'), 
                                  justify='left', anchor='w')
        SMTP_label.place(relx=0.05, rely=0.25, relheight=0.1)
        SMTP_entry = ctk.CTkEntry(general_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        SMTP_entry.insert(0, string=config['General']['SMTP'])
        SMTP_entry.place(relx=0.3, rely=0.25, relwidth=0.4, relheight=0.1)
        entry_list.append(SMTP_entry)
        
        POP3_label = ctk.CTkLabel(general_frame, text='POP3 port', font=('Calibri', 20, 'bold'), 
                                  justify='left', anchor='w')
        POP3_label.place(relx=0.05, rely=0.4, relheight=0.1)
        POP3_entry = ctk.CTkEntry(general_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        POP3_entry.insert(0, string=config['General']['POP3'])
        POP3_entry.place(relx=0.3, rely=0.4, relwidth=0.4, relheight=0.1)
        entry_list.append(POP3_entry)
        
        autoload_label = ctk.CTkLabel(general_frame, text='Autoload interval', font=('Calibri', 20, 'bold'), 
                                      justify='left', anchor='w')
        autoload_label.place(relx=0.05, rely=0.55, relheight=0.1)
        autoload_entry = ctk.CTkEntry(general_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        autoload_entry.insert(0, string=config['General']['Autoload'])
        autoload_entry.place(relx=0.3, rely=0.55, relwidth=0.4, relheight=0.1)
        entry_list.append(autoload_entry)
        
        # account
        account_frame = ctk.CTkFrame(settings_frame, corner_radius=0,
                                               fg_color='transparent')
        account_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        name_label = ctk.CTkLabel(account_frame, text='Your name', font=('Calibri', 20, 'bold'),
                                  justify='left', anchor='w')
        name_label.place(relx=0.05, rely=0.1, relheight=0.1)
        name_entry = ctk.CTkEntry(account_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        name_entry.place(relx=0.3, rely=0.1, relwidth=0.4, relheight=0.1)
        name_entry.insert(0, config['Account']['username'])
        entry_list.append(name_entry)
        
        usermail_label = ctk.CTkLabel(account_frame, text='Your mail', font=('Calibri', 20, 'bold'),
                                      justify='left', anchor='w')
        usermail_label.place(relx=0.05, rely=0.25, relheight=0.1)
        usermail_entry = ctk.CTkEntry(account_frame, corner_radius=15, border_width=0, font=('Calibri', 20))
        usermail_entry.place(relx=0.3, rely=0.25, relwidth=0.4, relheight=0.1)
        usermail_entry.insert(0, config['Account']['usermail'])
        entry_list.append(usermail_entry)
        
        password_label = ctk.CTkLabel(account_frame, text='Your password', font=('Calibri', 20, 'bold'),
                                      justify='left', anchor='w')
        password_label.place(relx=0.05, rely=0.4, relheight=0.1)
        password_entry = ctk.CTkEntry(account_frame, corner_radius=15, border_width=0, font=('Calibri', 20),
                                      show='*')
        password_entry.place(relx=0.3, rely=0.4, relwidth=0.4, relheight=0.1)
        password_entry.insert(0, config['Account']['password'])
        entry_list.append(password_entry)
        
        show_password_button = ctk.CTkButton(account_frame, text='Show password', font=('Calibri', 20, 'bold'),
                                             fg_color=('#9AD0C2', '#161A30'),
                                             text_color=('black', '#F0ECE5'),
                                             hover_color=('#2D9596', '#31304D'),
                                             command=lambda: self.show_password(password_entry))
        show_password_button.place(relx=0.75, rely=0.4, relheight=0.1)
        
        # filter
        filter_frame = ctk.CTkScrollableFrame(settings_frame, corner_radius=0,
                                              fg_color='transparent', 
                                              scrollbar_button_color=('#265073', '#31304D'),
                                              scrollbar_button_hover_color=('#2D9596', '#B6BBC4'))
        filter_frame.place(x=0, y=0, relwidth=1, relheight=1)
        
        self.add_filter_widget(entry_list, 'Subject', filter_frame)
        self.add_filter_widget(entry_list, 'Content', filter_frame)
        self.add_filter_widget(entry_list, 'From', filter_frame)
        
        # based on content
        
        # categories widgets
        # buttons
        general_button = ctk.CTkButton(categories_frame, text='General', font=('Calibri', 20, 'bold'),
                                       corner_radius=5, 
                                       fg_color='transparent',
                                       text_color=('#265073', '#F0ECE5'),
                                       hover_color=('#ECF4D6', '#161A30'),
                                       command=lambda: self.show_settings(general_button, general_frame))
        general_button.place(relx=0.5, rely=0.2, relwidth=0.7, relheight=0.1, anchor='n')
        
        account_button = ctk.CTkButton(categories_frame, text='Account', font=('Calibri', 20, 'bold'),
                                       corner_radius=5, 
                                       fg_color='transparent',
                                       text_color=('#265073', '#F0ECE5'),
                                       hover_color=('#ECF4D6', '#161A30'),
                                       command=lambda: self.show_settings(account_button, account_frame))
        account_button.place(relx=0.5, rely=0.35, relwidth=0.7, relheight=0.1, anchor='n')
        
        filter_button = ctk.CTkButton(categories_frame, text='Filter', font=('Calibri', 20, 'bold'),
                                      corner_radius=5, 
                                      fg_color='transparent',
                                      text_color=('#265073', '#F0ECE5'),
                                      hover_color=('#ECF4D6', '#161A30'),
                                      command=lambda: self.show_settings(filter_button, filter_frame))
        filter_button.place(relx=0.5, rely=0.5, relwidth=0.7, relheight=0.1, anchor='n')
        
        self.show_settings(general_button, general_frame)
    
    def add_filter_widget(self, entry_list: list, field_filter: str, filter_frame):
        field_filter_frame = ctk.CTkFrame(filter_frame, corner_radius=0, 
                                          fg_color='transparent')
        field_filter_frame.pack(expand=True, fill='x')
        
        subject_label = ctk.CTkLabel(field_filter_frame, text=f'Based on {field_filter.lower()}', font=('Calibri', 20, 'bold'),
                                     justify='left', anchor='w')
        subject_label.place(relx=0.05, rely=0.1, relheight=0.1)
        
        important_label = ctk.CTkLabel(field_filter_frame, text='Important folder', font=('Calibri', 18, 'bold'))
        important_label.place(relx=0.1, rely=0.25, relheight=0.15)
        important_entry = ctk.CTkEntry(field_filter_frame, corner_radius=15, border_width=0, font=('Calibri', 18))
        important_entry.place(relx=0.3, rely=0.25, relwidth=0.5, relheight=0.15)
        entry_list.append(important_entry)
        placeholder = ''
        for keyword in config['Filter'][field_filter]['Important']:
            placeholder += keyword + ', '    
        important_entry.insert(0, placeholder[:-2])
        
        college_label = ctk.CTkLabel(field_filter_frame, text='College folder', font=('Calibri', 18, 'bold'))       
        college_label.place(relx=0.1, rely=0.45, relheight=0.15)
        college_entry = ctk.CTkEntry(field_filter_frame, corner_radius=15, border_width=0, font=('Calibri', 18))
        college_entry.place(relx=0.3, rely=0.45, relwidth=0.5, relheight=0.15)
        entry_list.append(college_entry)
        placeholder = ''
        for keyword in config['Filter'][field_filter]['College']:
            placeholder += keyword + ', '    
        college_entry.insert(0, placeholder[:-2])
        
        spam_label = ctk.CTkLabel(field_filter_frame, text='Spam folder', font=('Calibri', 18, 'bold'))       
        spam_label.place(relx=0.1, rely=0.65, relheight=0.15)
        spam_entry = ctk.CTkEntry(field_filter_frame, corner_radius=15, border_width=0, font=('Calibri', 18))
        spam_entry.place(relx=0.3, rely=0.65, relwidth=0.5, relheight=0.15)
        entry_list.append(spam_entry)
        placeholder = ''
        for keyword in config['Filter'][field_filter]['Spam']:
            placeholder += keyword + ', '    
        spam_entry.insert(0, placeholder[:-2])
    
    def show_password(self, password_entry: ctk.CTkEntry):
        if password_entry.cget('show') == '*':
            password_entry.configure(show='')
        else: 
            password_entry.configure(show='*')
            
    def save_options(self, entry_list: list):
        changed = False
        # mailserver
        address = re.fullmatch(r'.+\..+\..+\..+', entry_list[0].get())
        if address != None:
            if not any(int(byte) < 0 or int(byte) > 255 for byte in address.string.split('.')):
                mail_server = entry_list[0].get()
                if config['General']['MailServer'] != mail_server:
                    config['General']['MailServer'] = mail_server
                    changed = True
        # ports
        smtp: str = entry_list[1].get()
        if smtp.isnumeric() and (int(smtp) > 0 and int(smtp) < 65536) and config['General']['SMTP'] != int(smtp):
            config['General']['SMTP'] = int(smtp)
            changed = True
        pop3: str = entry_list[2].get()
        if pop3.isnumeric() and (int(pop3) > 0 and int(pop3) < 65536) and config['General']['POP3'] != int(pop3):
            config['General']['POP3'] = int(pop3)
            changed = True
        # autoload
        autoload: str = entry_list[3].get()
        if autoload.isnumeric() and int(autoload) > 4 and config['General']['Autoload'] != int(autoload):
            config['General']['Autoload'] = int(autoload)
            changed = True
            
        # username
        username: str = entry_list[4].get()
        if config['Account']['username'] != username:
            config['Account']['username'] = username
            changed = True
        # usermail
        usermail: str = entry_list[5].get()
        if config['Account']['usermail'] != usermail:
            config['Account']['usermail'] = usermail
            changed = True
        # password
        password: str = entry_list[6].get()
        if config['Account']['password'] != password:
            config['Account']['password'] = password
            changed = True
        
        # subject filter
        important: list = [i for i in re.split(', |,', entry_list[7].get()) if i != '']
        if set(config['Filter']['Subject']['Important']) != set(important):
            config['Filter']['Subject']['Important'] = important
            changed = True
        college: list = [i for i in re.split(', |,', entry_list[8].get()) if i != '']
        if set(config['Filter']['Subject']['College']) != set(college):
            config['Filter']['Subject']['College'] = college
            changed = True
        spam: list = [i for i in re.split(', |,', entry_list[9].get()) if i != '']
        if set(config['Filter']['Subject']['Spam']) != set(spam):
            config['Filter']['Subject']['Spam'] = spam
            changed = True
        
        # content filter
        important: list = [i for i in re.split(', |,', entry_list[10].get()) if i != '']
        if set(config['Filter']['Content']['Important']) != set(important):
            config['Filter']['Content']['Important'] = important
            changed = True
        college: list = [i for i in re.split(', |,', entry_list[11].get()) if i != '']
        if set(config['Filter']['Content']['College']) != set(college):
            config['Filter']['Content']['College'] = college
            changed = True
        spam: list = [i for i in re.split(', |,', entry_list[12].get()) if i != '']
        if set(config['Filter']['Content']['Spam']) != set(spam):
            config['Filter']['Content']['Spam'] = spam
            changed = True
            
        # from filter
        important: list = [i for i in re.split(', |,', entry_list[13].get()) if i != '']
        if set(config['Filter']['From']['Important']) != set(important):
            config['Filter']['From']['Important'] = important
            changed = True
        college: list = [i for i in re.split(', |,', entry_list[14].get()) if i != '']
        if set(config['Filter']['From']['College']) != set(college):
            config['Filter']['From']['College'] = college
            changed = True
        spam: list = [i for i in re.split(', |,', entry_list[15].get()) if i != '']
        if set(config['Filter']['From']['Spam']) != set(spam):
            config['Filter']['From']['Spam'] = spam
            changed = True
            
        if changed:
            with open(os.path.join(os.getcwd(), 'config.json'), 'w') as config_file:
                json.dump(config, config_file, indent=4)
        
    def show_settings(self, setting_button: ctk.CTkButton, setting_frame: ctk.CTkFrame):
        if self.selected_button == setting_button:
            return
        
        # change old selected button
        if self.selected_button is not None:
            self.selected_button.configure(fg_color='transparent')
            
        # switch to new button
        self.selected_button = setting_button
        self.selected_button.configure(fg_color=('#ECF4D6', '#161A30'))
        setting_frame.lift()

    def toggle(self):
        if self.is_shown:
            self.lower()
            self.is_shown = False
        else:
            self.place(x=0, y=0, relwidth=1, relheight=1, anchor='nw')
            self.lift()
            self.is_shown = True

class MenuFrame(ctk.CTkFrame):
    def __init__(self, master, mail_list_frame: MailListFrame, setting_window: SettingWindow):
        super().__init__(master, corner_radius=0, fg_color=('#ECF4D6', '#161A30'), border_width=0)
        self.place(x=0, y=0, relwidth=0.2, relheight=1)
        self.mail_sending_window = None
        self.selected_folder_button = None
        self.mail_list_frame = mail_list_frame
        self.setting_window = setting_window
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
        sent_button = ctk.CTkButton(self, text='Sent', font=('Calibri', 14, 'bold'),
                                    text_color=('#265073', '#F0ECE5'),
                                    fg_color='transparent', 
                                    hover_color=('#9AD0C2', '#31304D'), 
                                    command=lambda: self.set_mail_list('Sent', sent_button))
        
        setting_button = ctk.CTkButton(self, text='Setting', font=('Calibri', 16, 'bold'),
                                       text_color=('#265073', '#F0ECE5'),
                                       fg_color='transparent', 
                                       hover_color=('#9AD0C2', '#31304D'), 
                                       command=self.setting_window.toggle)
        
        inbox_button.place(relx=0.5, rely=0.2, relwidth=0.6, relheight=0.05, anchor='n')
        important_button.place(relx=0.5, rely=0.26, relwidth=0.6, relheight=0.05, anchor='n')
        college_button.place(relx=0.5, rely=0.32, relwidth=0.6, relheight=0.05, anchor='n')
        spam_button.place(relx=0.5, rely=0.38, relwidth=0.6, relheight=0.05, anchor='n')
        sent_button.place(relx=0.5, rely=0.44, relwidth=0.6, relheight=0.05, anchor='n')
        setting_button.place(relx=0.5, rely=0.9, relwidth=0.7, relheight=0.05, anchor='s')
        
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
        if folder_name == 'Sent':
            command = f'SELECT * FROM sent'
        else:
            command = f'SELECT UIDL, SenderMail, Subject, IsRead FROM email WHERE Folder = "{folder_name}"'
        my_cursor.execute(command)
        mail_list = my_cursor.fetchall()
    return mail_list
        
def auto_load():   
    while True:
        get_message_thread = threading.Thread(target=clientPOP3.GetMessage)
        get_message_thread.start()
        get_message_thread.join()
        time.sleep(config['General']['Autoload'])
            
def main():
    # auto_load_thread = threading.Thread(target=auto_load, daemon=True)
    # auto_load_thread.start()
    App(WINDOW_WIDTH, WINDOW_HEIGHT)

if __name__ == '__main__':
    main()