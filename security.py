from cryptography.fernet import Fernet

# This is a 32-byte base64 encoded Fernet key
SECRET_KEY = b'v-L6_Y8X6G_7Y5Z_6V8W9X0Y1Z2A3B4C5D6E7F8G9H0='

class SecureComm:
    def __init__(self):
        try:
            self.cipher = Fernet(SECRET_KEY)
        except Exception as e:
            print(f"Encryption Key Error: {e}")
            raise

    def encrypt(self, message: str) -> bytes:
        return self.cipher.encrypt(message.encode())

    def decrypt(self, token: bytes) -> str:
        return self.cipher.decrypt(token).decode()