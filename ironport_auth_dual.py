import thread
import ironport_proxy_auth as ipa
import ironport_auth as ia
import sys
import getpass

def create_threads(username, password):
    try:
        thread.start_new_thread(ia.main, (username, password, ))
        thread.start_new_thread(ipa.main, (username, password, ))
    except:
        print "Error: unable to start thread"
        exit(0)

def get_cred():
    print("Username: "),
    username = sys.stdin.readline()[:-1]
    password = getpass.getpass()
    return (username, password)

def main():
    if len(sys.argv) == 3:
        username = sys.argv[1]
        password = sys.argv[2]
    elif len(sys.argv) == 1:
        username, password = get_cred()
    else:
        print "Invalid arguments"
        return
    create_threads(username, password)
    while 1:
        pass

if __name__ == "__main__":
    main()