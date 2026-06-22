# Simple Password Manager (Local Encrypted File)

A secure, local password manager that stores your passwords in an encrypted file using the `cryptography` library.

## Features

- 🔐 **Strong Encryption**: Uses Fernet symmetric encryption with PBKDF2 key derivation
- 🔑 **Single Master Password**: Access all your passwords with one master password
- 📁 **Local Storage**: All data stays on your machine - no cloud storage
- 🔒 **Secure Password Generation**: Generate strong random passwords
- 📝 **Organize**: Store username, password, and notes for each service
- 🔍 **Search**: Quickly find services by name
- 📤 **Import/Export**: Backup or transfer your passwords (use with caution)

## Installation

1. Clone or download this repository
2. Install the required dependency:

```bash
pip install -r requirements.txt
