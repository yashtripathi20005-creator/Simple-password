"""
Encryption and decryption utilities using Fernet symmetric encryption.
"""
import os
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import config


def generate_key_from_password(master_password: str, salt: bytes) -> bytes:
    """
    Generate a Fernet key from a master password and salt.
    
    Args:
        master_password: The master password string
        salt: Random salt bytes
    
    Returns:
        Base64 encoded key suitable for Fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=config.KEY_SIZE,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key


def generate_salt() -> bytes:
    """Generate a random salt."""
    return os.urandom(config.SALT_SIZE)


def encrypt_data(data: str, key: bytes) -> bytes:
    """
    Encrypt data using Fernet.
    
    Args:
        data: String data to encrypt
        key: Fernet key
    
    Returns:
        Encrypted data as bytes
    """
    f = Fernet(key)
    return f.encrypt(data.encode())


def decrypt_data(encrypted_data: bytes, key: bytes) -> str:
    """
    Decrypt data using Fernet.
    
    Args:
        encrypted_data: Encrypted data bytes
        key: Fernet key
    
    Returns:
        Decrypted string
    """
    f = Fernet(key)
    return f.decrypt(encrypted_data).decode()


def load_key_from_file(key_file: str) -> bytes:
    """
    Load the encryption key from a file.
    
    Args:
        key_file: Path to the key file
    
    Returns:
        Encryption key as bytes
    """
    with open(key_file, 'rb') as f:
        data = f.read()
        # File format: salt (32 bytes) + key (base64 encoded)
        salt = data[:config.SALT_SIZE]
        key = data[config.SALT_SIZE:]
        return key, salt


def save_key_to_file(key: bytes, salt: bytes, key_file: str) -> None:
    """
    Save the encryption key and salt to a file.
    
    Args:
        key: Encryption key
        salt: Salt used to generate the key
        key_file: Path to save the key file
    """
    with open(key_file, 'wb') as f:
        f.write(salt + key)


def initialize_encryption(master_password: str) -> bytes:
    """
    Initialize encryption by generating a key from the master password.
    
    Args:
        master_password: Master password string
    
    Returns:
        Encryption key
    """
    salt = generate_salt()
    key = generate_key_from_password(master_password, salt)
    save_key_to_file(key, salt, config.KEY_FILE)
    return key


def load_encryption_key(master_password: str) -> bytes:
    """
    Load the encryption key from file using the master password.
    
    Args:
        master_password: Master password string
    
    Returns:
        Encryption key
    
    Raises:
        ValueError: If the key file doesn't exist or password is incorrect
    """
    if not os.path.exists(config.KEY_FILE):
        raise ValueError("Key file not found. Please initialize the password manager.")
    
    with open(config.KEY_FILE, 'rb') as f:
        data = f.read()
        salt = data[:config.SALT_SIZE]
        key = generate_key_from_password(master_password, salt)
    
    # Verify the key is correct by trying to load the password file
    return key
