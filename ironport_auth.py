import urllib
import httplib
import sys
import getpass
import logging
import time
import re
import socket
import atexit

RETRY_INTERVAL = 30

def check_status():
    logger = logging.getLogger("auth")
    try:
        conn = httplib.HTTPConnection("authenticate.iitk.ac.in")
        conn.request("GET", "/netaccess/connstatus.html")
        response = conn.getresponse()
        data = response.read()
        if response.status == 200:
            sid = re.search(r'name=sid value="([0-9a-f]+)"', data, re.IGNORECASE).group(1)
            if 'You are not logged in' in data:
                return ('Not logged in', sid)
            elif 'You are logged in' in data:
                return ('Logged in', sid)
        else:
            logger.info('Error checking status. Unexpected response %d. Retrying in %d seconds.' % (response.status, RETRY_INTERVAL))
    except (httplib.HTTPException, socket.error) as e:
        logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, RETRY_INTERVAL))
        return (None, None)
    finally:
        conn.close()

def attemp_logout(sid):
    logger = logging.getLogger("auth")
    params = urllib.urlencode({'sid': sid, 'logout': 'Log Out Now'})
    headers = {"Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    try:
        postconn = httplib.HTTPSConnection('authenticate.iitk.ac.in')
        postconn.request("POST", "/netaccess/connstatus.html", params, headers)

        # Get the response
        postResponse = postconn.getresponse()
        postData = postResponse.read()
        if postResponse.status != 200:
            logger.info("Error loggin in. Server responded with status code %d. Retrying in %d seconds." % (postResponse.status, RETRY_INTERVAL))
        else:
            sid = re.search(r'name=sid value="([0-9a-f]+)"', postData, re.IGNORECASE).group(1)
            return req_login_page(sid)
    except (httplib.HTTPException, socket.error) as e:
        logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, RETRY_INTERVAL))
        return None
    finally:
        postconn.close()

def atexit_procedure():
    status, sid = check_status()
    if status == "Logged in" and sid is not None:
        attemp_logout(sid)
    print("User logged out.")

def req_login_page(sid):
    logger = logging.getLogger("auth")
    params = urllib.urlencode({'sid': sid, 'login': 'Log In Now'})
    headers = {"Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}
    try:
        postconn = httplib.HTTPSConnection('authenticate.iitk.ac.in')
        postconn.request("POST", "/netaccess/connstatus.html", params, headers)

        # Get the response
        postResponse = postconn.getresponse()
        postData = postResponse.read()
        if postResponse.status != 200:
            logger.info("Error loggin in. Server responded with status code %d. Retrying in %d seconds." % (postResponse.status, RETRY_INTERVAL))
        else:
            sid = re.search(r'name=sid value="([0-9a-f]+)"', postData, re.IGNORECASE).group(1)
            return sid
    except (httplib.HTTPException, socket.error) as e:
        logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, RETRY_INTERVAL))
        return None
    finally:
        postconn.close()


def attempt_login(username, password):
    logger = logging.getLogger("auth")

    status, sid = check_status()
    
    if sid is None:
        return

    if status == "Logged in":
        sid = attemp_logout(sid)
    elif status == "Not logged in":
        sid = req_login_page(sid)

    if sid is None:
        return

    params = urllib.urlencode({'username': username, 'password': password, 'sid': sid})
    headers = {"Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/plain"}

    try:
        postconn = httplib.HTTPSConnection('authenticate.iitk.ac.in')
        postconn.request("POST", "/netaccess/loginuser.html", params, headers)

        # Get the response
        postResponse = postconn.getresponse()
        postData = postResponse.read()
        if postResponse.status != 200:
            logger.info("Error loggin in. Server responded with status code %d. Retrying in %d seconds." % (postResponse.status, RETRY_INTERVAL))
        else:
            if 'Credentials Rejected' in postData:
                print("Username or password incorrect.")
                exit(0)
            else:
                logger.info("Currently logged in.")
    except (httplib.HTTPException, socket.error) as e:
        logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, RETRY_INTERVAL))
    finally:
        postconn.close()

def get_cred():
    print("Username: "),
    username = sys.stdin.readline()[:-1]
    password = getpass.getpass()
    return (username, password)

def keep_logging_in(username, password):
    init_logger()
    atexit.register(atexit_procedure)
    while True:
        attempt_login(username, password)
        time.sleep(RETRY_INTERVAL)

def init_logger():
    logger = logging.getLogger("auth")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def main():
    (username, password) = get_cred()
    keep_logging_in(username, password)

def main_debug():
    keep_logging_in(sys.argv[1], sys.argv[2])

if __name__=='__main__':
    if(len(sys.argv) > 1):
        main_debug()
    else:
        main()