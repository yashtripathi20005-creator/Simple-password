"""
Core password manager functionality.
"""
import os
import json
import base64
from typing import Dict, Optional, List
import config
import encryption


class PasswordManager:
    """Main password manager class."""
    
    def __init__(self, master_password: str):
        """
        Initialize the password manager.
        
        Args:
            master_password: Master password for encryption
        """
        self.master_password = master_password
        self.key = None
        self.passwords = {}
        self._load_or_initialize()
    
    def _load_or_initialize(self) -> None:
        """Load existing password database or initialize a new one."""
        if os.path.exists(config.KEY_FILE) and os.path.exists(config.PASSWORD_FILE):
            self._load_database()
        else:
            self._initialize_database()
    
    def _initialize_database(self) -> None:
        """Initialize a new password database."""
        self.key = encryption.initialize_encryption(self.master_password)
        self.passwords = {}
        self._save_passwords()
        print("✓ Password manager initialized successfully!")
    
    def _load_database(self) -> None:
        """Load the existing password database."""
        try:
            self.key = encryption.load_encryption_key(self.master_password)
            self._load_passwords()
            print("✓ Database loaded successfully!")
        except ValueError as e:
            print(f"✗ Error: {e}")
            raise
    
    def _load_passwords(self) -> None:
        """Load and decrypt passwords from file."""
        if not os.path.exists(config.PASSWORD_FILE):
            self.passwords = {}
            return
        
        with open(config.PASSWORD_FILE, 'rb') as f:
            encrypted_data = f.read()
        
        try:
            decrypted_data = encryption.decrypt_data(encrypted_data, self.key)
            self.passwords = json.loads(decrypted_data)
        except Exception as e:
            print(f"✗ Error loading passwords: {e}")
            self.passwords = {}
    
    def _save_passwords(self) -> None:
        """Encrypt and save passwords to file."""
        # Ensure directory exists
        os.makedirs(config.DATA_DIR, exist_ok=True)
        
        json_data = json.dumps(self.passwords, indent=2, sort_keys=True)
        encrypted_data = encryption.encrypt_data(json_data, self.key)
        
        with open(config.PASSWORD_FILE, 'wb') as f:
            f.write(encrypted_data)
    
    def add_password(self, service: str, username: str, password: str, notes: str = "") -> None:
        """
        Add or update a password entry.
        
        Args:
            service: Service name (e.g., "gmail.com")
            username: Username or email
            password: Password
            notes: Optional notes
        """
        self.passwords[service] = {
            'username': username,
            'password': password,
            'notes': notes
        }
        self._save_passwords()
        print(f"✓ Password for '{service}' saved successfully!")
    
    def get_password(self, service: str) -> Optional[Dict]:
        """
        Retrieve a password entry.
        
        Args:
            service: Service name
        
        Returns:
            Dictionary with username, password, and notes, or None if not found
        """
        return self.passwords.get(service)
    
    def delete_password(self, service: str) -> bool:
        """
        Delete a password entry.
        
        Args:
            service: Service name
        
        Returns:
            True if deleted, False if not found
        """
        if service in self.passwords:
            del self.passwords[service]
            self._save_passwords()
            print(f"✓ Password for '{service}' deleted successfully!")
            return True
        else:
            print(f"✗ Service '{service}' not found.")
            return False
    
    def list_services(self) -> List[str]:
        """List all stored service names."""
        return sorted(self.passwords.keys())
    
    def search_services(self, query: str) -> List[str]:
        """Search for services containing the query string."""
        query_lower = query.lower()
        return sorted([s for s in self.passwords.keys() if query_lower in s.lower()])
    
    def generate_password(self, length: int = config.DEFAULT_PASSWORD_LENGTH) -> str:
        """
        Generate a strong random password.
        
        Args:
            length: Password length
        
        Returns:
            Generated password string
        """
        import random
        import string
        
        # Ensure at least one character from each category
        categories = [
            string.ascii_lowercase,
            string.ascii_uppercase,
            string.digits,
            "!@#$%^&*()_+-=[]{}|;:,.<>?/~`"
        ]
        
        # Ensure minimum length for all categories
        if length < len(categories):
            length = len(categories)
        
        # Pick one from each category
        password_chars = [random.choice(cat) for cat in categories]
        
        # Fill the rest with random characters
        all_chars = ''.join(categories)
        password_chars.extend(random.choice(all_chars) for _ in range(length - len(categories)))
        
        # Shuffle the password
        random.shuffle(password_chars)
        return ''.join(password_chars)
    
    def export_passwords(self, filename: str) -> None:
        """
        Export passwords to a JSON file (unencrypted - use with caution).
        
        Args:
            filename: Output filename
        """
        with open(filename, 'w') as f:
            json.dump(self.passwords, f, indent=2, sort_keys=True)
        print(f"✓ Passwords exported to {filename}")
    
    def import_passwords(self, filename: str, overwrite: bool = False) -> None:
        """
        Import passwords from a JSON file.
        
        Args:
            filename: Input filename
            overwrite: Whether to overwrite existing entries
        """
        with open(filename, 'r') as f:
            imported = json.load(f)
        
        if not overwrite:
            # Merge, preserving existing entries
            self.passwords.update(imported)
        else:
            self.passwords = imported
        
        self._save_passwords()
        print(f"✓ Passwords imported from {filename}")
