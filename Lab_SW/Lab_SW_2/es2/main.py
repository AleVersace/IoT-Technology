import Api

def menu():
    command = str(input('Available command:\nBroker: the message broker\nDevices: all the registered devices\nDevice: specific device with deviceID as input\nUsers: all the registered users\nUser: specific user with userID as input\nServices: all the registered services\nService: specific service with serviceID as input\nQuit: exit\n'))
    command.lower()
    if command == 'broker':
        return 1
    elif command == 'devices':
        return 2
    elif command == 'device':
        return 3
    elif command == 'users':
        return 4
    elif command == 'user':
        return 5
    elif command == "services":
        return 6
    elif command == "service":
        return 7
    elif command == 'quit':
        return 0
    else:
        return -1

# Command to request translation
def apis(api, command):
    if command == 1:
        api.broker()
    elif command == 2:
        api.devices()
    elif command == 3:
        api.device()
    elif command == 4:
        api.users()
    elif command == 5:
        api.user()
    elif command == 6:
        api.service()
    elif command == 7:
        api.services()
    else:
        print('\nNot a valid command!')
        

if __name__ == "__main__":
    
    while True:
        c = menu()
        if c == 0:
            break
        else:
            e = Api.Api()
            apis(e, c)
    
    print('\nEnd of program')

