"""
Command-line interface for the password manager.
"""
import sys
import os
import getpass
from typing import Optional
import config
from password_manager import PasswordManager


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header():
    """Print the application header."""
    print("=" * 60)
    print("         🔐 SIMPLE PASSWORD MANAGER (Local Encrypted File)")
    print("=" * 60)
    print()


def get_master_password() -> str:
    """
    Prompt for master password securely.
    
    Returns:
        Master password string
    """
    while True:
        password = getpass.getpass("Enter master password: ")
        if len(password) < config.MIN_MASTER_PASSWORD_LENGTH:
            print(f"✗ Password must be at least {config.MIN_MASTER_PASSWORD_LENGTH} characters long.")
            continue
        return password


def setup_password_manager() -> Optional[PasswordManager]:
    """
    Initialize or load the password manager.
    
    Returns:
        PasswordManager instance or None if failed
    """
    print_header()
    
    if not os.path.exists(config.KEY_FILE):
        print("🔐 First-time setup: Creating new password manager...")
        print(f"Your passwords will be stored in: {config.DATA_DIR}")
        print("IMPORTANT: Remember your master password! It cannot be recovered if lost.")
        print()
        master_password = get_master_password()
        return PasswordManager(master_password)
    else:
        print("🔐 Loading existing password manager...")
        attempts = 0
        while attempts < config.MAX_LOGIN_ATTEMPTS:
            try:
                master_password = get_master_password()
                return PasswordManager(master_password)
            except ValueError:
                attempts += 1
                remaining = config.MAX_LOGIN_ATTEMPTS - attempts
                print(f"✗ Incorrect master password. {remaining} attempts remaining.")
        
        print("✗ Too many failed attempts. Exiting...")
        return None


def print_menu():
    """Print the main menu."""
    print("\n" + "-" * 60)
    print("MENU:")
    print("  1. Add/Update password")
    print("  2. Get password")
    print("  3. Delete password")
    print("  4. List all services")
    print("  5. Search services")
    print("  6. Generate random password")
    print("  7. Export passwords (UNENCRYPTED)")
    print("  8. Import passwords")
    print("  9. Change master password")
    print("  0. Exit")
    print("-" * 60)


def add_password_interactive(pm: PasswordManager):
    """Interactive add password function."""
    clear_screen()
    print_header()
    print("ADD PASSWORD\n")
    
    service = input("Service name (e.g., gmail.com): ").strip()
    if not service:
        print("✗ Service name cannot be empty.")
        return
    
    username = input("Username/Email: ").strip()
    if not username:
        print("✗ Username cannot be empty.")
        return
    
    generate = input("Generate random password? (y/n): ").lower().strip()
    if generate == 'y':
        length = input(f"Password length (default {config.DEFAULT_PASSWORD_LENGTH}): ").strip()
        length = int(length) if length else config.DEFAULT_PASSWORD_LENGTH
        password = pm.generate_password(length)
        print(f"Generated password: {password}")
    else:
        password = getpass.getpass("Password: ").strip()
        if not password:
            print("✗ Password cannot be empty.")
            return
    
    notes = input("Notes (optional): ").strip()
    
    pm.add_password(service, username, password, notes)


def get_password_interactive(pm: PasswordManager):
    """Interactive get password function."""
    clear_screen()
    print_header()
    print("GET PASSWORD\n")
    
    service = input("Service name: ").strip()
    if not service:
        print("✗ Service name cannot be empty.")
        return
    
    entry = pm.get_password(service)
    if entry:
        print("\n" + "=" * 60)
        print(f"Service: {service}")
        print(f"Username: {entry['username']}")
        print(f"Password: {entry['password']}")
        if entry.get('notes'):
            print(f"Notes: {entry['notes']}")
        print("=" * 60)
        print("\n✓ Password retrieved! (It has been copied to clipboard? Currently not, but you can select it.)")
    else:
        print(f"✗ Service '{service}' not found.")


def list_services_interactive(pm: PasswordManager):
    """Interactive list services function."""
    clear_screen()
    print_header()
    print("LIST SERVICES\n")
    
    services = pm.list_services()
    if services:
        print(f"Found {len(services)} service(s):")
        for i, service in enumerate(services, 1):
            print(f"  {i}. {service}")
    else:
        print("No services saved yet.")


def search_services_interactive(pm: PasswordManager):
    """Interactive search services function."""
    clear_screen()
    print_header()
    print("SEARCH SERVICES\n")
    
    query = input("Search query: ").strip()
    if not query:
        print("✗ Search query cannot be empty.")
        return
    
    results = pm.search_services(query)
    if results:
        print(f"Found {len(results)} result(s):")
        for i, service in enumerate(results, 1):
            entry = pm.get_password(service)
            print(f"  {i}. {service} - {entry['username']}")
    else:
        print("No matching services found.")


def delete_password_interactive(pm: PasswordManager):
    """Interactive delete password function."""
    clear_screen()
    print_header()
    print("DELETE PASSWORD\n")
    
    service = input("Service name to delete: ").strip()
    if not service:
        print("✗ Service name cannot be empty.")
        return
    
    confirm = input(f"Are you sure you want to delete '{service}'? (y/n): ").lower().strip()
    if confirm == 'y':
        pm.delete_password(service)


def generate_password_interactive(pm: PasswordManager):
    """Interactive generate password function."""
    clear_screen()
    print_header()
    print("GENERATE PASSWORD\n")
    
    length = input(f"Password length (default {config.DEFAULT_PASSWORD_LENGTH}): ").strip()
    length = int(length) if length else config.DEFAULT_PASSWORD_LENGTH
    
    password = pm.generate_password(length)
    print(f"\nGenerated password: {password}")
    print("\n✓ Password generated! (Copy it now.)")


def export_passwords_interactive(pm: PasswordManager):
    """Interactive export passwords function."""
    clear_screen()
    print_header()
    print("EXPORT PASSWORDS\n")
    print("⚠️  WARNING: This will export passwords in PLAIN TEXT!")
    print("   Make sure to delete the file after use.\n")
    
    filename = input("Export filename (e.g., passwords_export.json): ").strip()
    if not filename:
        filename = "passwords_export.json"
    
    confirm = input(f"Export to '{filename}'? (y/n): ").lower().strip()
    if confirm == 'y':
        pm.export_passwords(filename)


def import_passwords_interactive(pm: PasswordManager):
    """Interactive import passwords function."""
    clear_screen()
    print_header()
    print("IMPORT PASSWORDS\n")
    
    filename = input("Import filename: ").strip()
    if not filename:
        print("✗ Filename cannot be empty.")
        return
    
    if not os.path.exists(filename):
        print(f"✗ File '{filename}' not found.")
        return
    
    overwrite = input("Overwrite existing entries? (y/n): ").lower().strip() == 'y'
    
    try:
        pm.import_passwords(filename, overwrite)
    except Exception as e:
        print(f"✗ Error importing: {e}")


def change_master_password_interactive(pm: PasswordManager):
    """Interactive change master password function."""
    clear_screen()
    print_header()
    print("CHANGE MASTER PASSWORD\n")
    print("⚠️  This will re-encrypt all your passwords with the new master password.")
    print("   Make sure you remember your current master password!\n")
    
    confirm = input("Continue? (y/n): ").lower().strip()
    if confirm != 'y':
        return
    
    # Re-encrypt all data with new password
    try:
        # Get current data
        current_data = pm.passwords
        
        # Create new key with new master password
        new_password = getpass.getpass("New master password: ")
        confirm_password = getpass.getpass("Confirm new master password: ")
        
        if new_password != confirm_password:
            print("✗ Passwords do not match.")
            return
        
        if len(new_password) < config.MIN_MASTER_PASSWORD_LENGTH:
            print(f"✗ Password must be at least {config.MIN_MASTER_PASSWORD_LENGTH} characters long.")
            return
        
        # Re-encrypt with new key
        import encryption
        import json
        import os
        
        # Generate new key
        salt = encryption.generate_salt()
        new_key = encryption.generate_key_from_password(new_password, salt)
        
        # Re-encrypt data
        json_data = json.dumps(current_data, indent=2, sort_keys=True)
        encrypted_data = encryption.encrypt_data(json_data, new_key)
        
        # Save new key
        encryption.save_key_to_file(new_key, salt, config.KEY_FILE)
        
        # Save re-encrypted data
        with open(config.PASSWORD_FILE, 'wb') as f:
            f.write(encrypted_data)
        
        # Update the instance
        pm.key = new_key
        
        print("✓ Master password changed successfully!")
    except Exception as e:
        print(f"✗ Error changing master password: {e}")


def main():
    """Main application entry point."""
    # Create data directory if it doesn't exist
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    # Setup password manager
    pm = setup_password_manager()
    if not pm:
        sys.exit(1)
    
    # Main loop
    while True:
        print_menu()
        choice = input("\nEnter your choice: ").strip()
        
        if choice == '0':
            print("\nGoodbye! 👋")
            sys.exit(0)
        elif choice == '1':
            add_password_interactive(pm)
        elif choice == '2':
            get_password_interactive(pm)
        elif choice == '3':
            delete_password_interactive(pm)
        elif choice == '4':
            list_services_interactive(pm)
        elif choice == '5':
            search_services_interactive(pm)
        elif choice == '6':
            generate_password_interactive(pm)
        elif choice == '7':
            export_passwords_interactive(pm)
        elif choice == '8':
            import_passwords_interactive(pm)
        elif choice == '9':
            change_master_password_interactive(pm)
        else:
            print("✗ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nGoodbye! 👋")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
