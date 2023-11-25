import clientSMTP
import clientPOP3
import threading
import time
import json

def main():
    def auto_load():
        with open('config.json', 'r') as fin:
            config = json.load(fin)
            interval = config['General']['Autoload']
        
        while True:
            get_message_thread = threading.Thread(target=clientPOP3.GetMessage)
            get_message_thread.start()
            get_message_thread.join()
            time.sleep(interval)
            
    auto_load_thread = threading.Thread(target=auto_load, daemon=True)
    auto_load_thread.start()
    
    while True:
        print("Options:")
        print("1. Send email")
        print("2. Check mailbox")
        print("3. Quit")
        choice = int(input("Input your choice: "))
        
        match choice:
            case 1:
                clientSMTP.SendMail()
            case 2:
                clientPOP3.CheckMail()
            case 3:
                return
            case _:
                print('Invalid choice!\n')
        
if __name__ == '__main__':
    main()