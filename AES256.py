import string
import random
import base64
from Cryptodome.Cipher import AES
from Cryptodome.Random import get_random_bytes
import struct
import os


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