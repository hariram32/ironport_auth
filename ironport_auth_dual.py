from threading import Thread
import ironport_proxy_auth as ipa
import ironport_auth as ia
import sys
import getpass

def create_threads(username, password):
    try:
        t1 = Thread(target=ia.main, args=(username, password, ))
        t2 = Thread(target=ipa.main, args=(username, password, ))
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except:
        print "Error: unable to start thread"
        sys.exit(0)

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


if __name__ == "__main__":
    main()