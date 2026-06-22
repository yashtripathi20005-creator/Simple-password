"""
Configuration settings for the password manager.
"""
import os

# File paths
DATA_DIR = os.path.join(os.path.expanduser("~"), ".password_manager")
PASSWORD_FILE = os.path.join(DATA_DIR, "passwords.enc")
KEY_FILE = os.path.join(DATA_DIR, "key.key")

# Encryption settings
SALT_SIZE = 32
KEY_SIZE = 32
NONCE_SIZE = 12

# Password generation settings
DEFAULT_PASSWORD_LENGTH = 16
PASSWORD_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?/~`"

# Master password settings
MIN_MASTER_PASSWORD_LENGTH = 8
MAX_LOGIN_ATTEMPTS = 3
