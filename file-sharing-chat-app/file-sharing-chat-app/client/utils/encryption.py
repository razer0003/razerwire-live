from cryptography.fernet import Fernet

def generate_key():
    return Fernet.generate_key()

def load_key(key_path):
    with open(key_path, "rb") as key_file:
        return key_file.read()

def encrypt_message(message, key):
    f = Fernet(key)
    encrypted_message = f.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    f = Fernet(key)
    decrypted_message = f.decrypt(encrypted_message).decode()
    return decrypted_message