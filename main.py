import clientSMPT
import clientPOP3

def main():
    while True:
        print("Options:")
        print("1. Send email")
        print("2. Check mailbox")
        print("3. Quit")
        choice = int(input("Input your choice: "))
        
        match choice:
            case 1:
                clientSMPT.SendMail()
            case 2:
                clientPOP3.GetMessage()
                clientPOP3.CheckMail()
            case 3:
                return
            case _:
                print('Invalid choice!\n')
        
        

if __name__ == '__main__':
    main()