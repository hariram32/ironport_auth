import sys
import urllib2
import time
import socket
import httplib
import ssl
import re
from base64 import b64encode
import requests
import logging
import warnings
warnings.filterwarnings("ignore")

attempt = 0

ERROR_INTERVAL = 5
RETRY_INTERVAL = 100

def init_logger():
    logger = logging.getLogger("proxy_auth")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s [IRONPORT PROXY AUTH]")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

def get_cred():
    print("Username: "),
    username = sys.stdin.readline()[:-1]
    password = getpass.getpass()
    return (username, password)

def get_login_url():
    logger = logging.getLogger("proxy_auth")
    try:
        gcontext = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        conn = httplib.HTTPSConnection("amazon.com", context=gcontext)
        conn.request("GET", "/")
        response = conn.getresponse()
        data = response.read()
        match = re.search(r'href="(https://ironport1\.iitk\.ac\.in/[A-Z0-9]+/https://amazon.com/)"', data, re.IGNORECASE)
        if match is not None:
            return match.group(1)
        else:
            return "Logged in"
    except (httplib.HTTPException, socket.error) as e:
        logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, ERROR_INTERVAL))
        return "Error"

def attemp_login(username, password):
    global attempt
    logger = logging.getLogger("proxy_auth")
    login_url = get_login_url()

    if login_url == "Logged in":
        logger.info("User logged in. Retrying in %d seconds." % RETRY_INTERVAL)
        return RETRY_INTERVAL
    elif login_url == "Error":
        return ERROR_INTERVAL
    else:
        try:
            data = requests.get(login_url, auth=(username, password),  verify=False).content
            if attempt == 1:
                logger.info("Failed to login. Please check your username or password.")
                attempt = 0
                return ERROR_INTERVAL
            else:
                attempt = 1
                logger.info("Attempting login with passed credentials....")
                return ERROR_INTERVAL
        except Exception as e:
            logger.info("Caught exception: %s. Please check your internet connection/gateway. Retrying in %d seconds." % (e, ERROR_INTERVAL))
            return ERROR_INTERVAL

def keep_trying(username, password):
    while True:
        time.sleep(attemp_login(username, password))


def main(username=None, password=None):
    init_logger()
    if username is None or password is None:
        if len(sys.argv) == 3:
            username = sys.argv[1]
            password = sys.argv[2]
        elif len(sys.argv) == 1:
            username, password = get_cred()
        else:
            print "Invalid arguments"
            return
    keep_trying(username, password)

if __name__ == "__main__":
    main()