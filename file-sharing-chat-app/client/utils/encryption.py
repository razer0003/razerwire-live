from cryptography.fernet import Fernet

def generate_key():
    """Generate a new encryption key."""
    return Fernet.generate_key()

def load_key(key_path):
    """Load the encryption key from a file."""
    with open(key_path, 'rb') as key_file:
        return key_file.read()

def encrypt_message(message, key):
    """Encrypt a message using the provided key."""
    fernet = Fernet(key)
    encrypted_message = fernet.encrypt(message.encode())
    return encrypted_message

def decrypt_message(encrypted_message, key):
    """Decrypt a message using the provided key."""
    fernet = Fernet(key)
    decrypted_message = fernet.decrypt(encrypted_message).decode()
    return decrypted_message