import clientSMPT

def main():
    while True:
        print("Options:")
        print("1. Send email")
        print("2. Check mailbox")
        print("3. Quit")
        # choice = int(input("Input your choice: "))
        choice = 1
        
        match choice:
            case 1:
                clientSMPT.SendMail()
                return
            case 2:
                pass
            case 3:
                return
            case _:
                print('Invalid choice!\n')
        
        

if __name__ == '__main__':
    main()