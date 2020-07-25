from Cryptodome.PublicKey import RSA
from Cryptodome.Cipher import PKCS1_OAEP
import binascii


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