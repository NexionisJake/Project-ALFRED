"""
Encryption utilities for ALFRED's knowledge base.
Uses Fernet symmetric encryption with password-derived keys.
"""

import os
import base64
import getpass
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from colorama import Fore

# Salt for key derivation (can be stored alongside encrypted file)
# In production, this should be unique per-file and stored with ciphertext
DEFAULT_SALT = b'alfred_secure_salt_2026'


def derive_key(password: str, salt: bytes = DEFAULT_SALT) -> bytes:
    """
    Derives a Fernet-compatible key from a password using PBKDF2.
    
    Args:
        password: User's password string
        salt: Salt for key derivation (default provided, but unique salt recommended)
    
    Returns:
        Base64-encoded key suitable for Fernet
    """
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # OWASP 2023 recommendation
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_content(content: str, password: str) -> bytes:
    """
    Encrypts string content using Fernet encryption.
    
    Args:
        content: Plain text to encrypt
        password: Encryption password
    
    Returns:
        Encrypted bytes
    """
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.encrypt(content.encode('utf-8'))


def decrypt_content(encrypted_data: bytes, password: str) -> str:
    """
    Decrypts Fernet-encrypted content.
    
    Args:
        encrypted_data: Encrypted bytes
        password: Decryption password
    
    Returns:
        Decrypted string
    
    Raises:
        InvalidToken: If password is wrong or data is corrupted
    """
    key = derive_key(password)
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_data).decode('utf-8')


def encrypt_file(filepath: str, password: str, output_path: str = None) -> str:
    """
    Encrypts a file and saves to .enc extension.
    
    Args:
        filepath: Path to plain text file
        password: Encryption password
        output_path: Optional output path (defaults to filepath + .enc)
    
    Returns:
        Path to encrypted file
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    encrypted = encrypt_content(content, password)
    
    if output_path is None:
        output_path = filepath + '.enc'
    
    with open(output_path, 'wb') as f:
        f.write(encrypted)
    
    return output_path


def decrypt_file(filepath: str, password: str) -> str:
    """
    Decrypts an encrypted file and returns content.
    
    Args:
        filepath: Path to encrypted file
        password: Decryption password
    
    Returns:
        Decrypted content string
    """
    with open(filepath, 'rb') as f:
        encrypted_data = f.read()
    
    return decrypt_content(encrypted_data, password)


class SecureKnowledgeBase:
    """
    Secure wrapper for the knowledge base with encryption support.
    Supports both plain text (legacy) and encrypted formats.
    """
    
    def __init__(self, brain_path: str, password: str = None):
        """
        Initialize SecureKnowledgeBase.
        
        Args:
            brain_path: Path to brain.txt (or brain.txt.enc)
            password: Password for encrypted files (None for plain text)
        """
        self.brain_path = brain_path
        self.encrypted_path = brain_path + '.enc'
        self.password = password
        self._content = None
        self._is_encrypted = os.path.exists(self.encrypted_path)
    
    def _get_password(self) -> str:
        """Get password from environment or prompt user (if interactive)."""
        if self.password:
            return self.password
        
        # Try environment variable first
        env_password = os.getenv('ALFRED_BRAIN_PASSWORD')
        if env_password:
            return env_password
        
        # Check if we're in an interactive terminal
        # If not interactive (e.g., running in tests), raise an error instead of blocking
        import sys
        if not sys.stdin.isatty():
            raise RuntimeError("Password required but running in non-interactive mode. Set ALFRED_BRAIN_PASSWORD environment variable.")
        
        # Prompt user (only works in interactive mode)
        return getpass.getpass(Fore.CYAN + "Enter knowledge base password: " + Fore.RESET)
    
    def load(self) -> str:
        """
        Load knowledge base content (handles both encrypted and plain).
        
        Returns:
            Content string
        """
        if self._content is not None:
            return self._content
        
        if self._is_encrypted:
            try:
                password = self._get_password()
                self._content = decrypt_file(self.encrypted_path, password)
                print(Fore.GREEN + "✓ Knowledge base decrypted successfully")
            except InvalidToken:
                print(Fore.RED + "✗ Invalid password for knowledge base")
                return ""
            except Exception as e:
                print(Fore.RED + f"✗ Error loading encrypted knowledge base: {e}")
                return ""
        else:
            # Fall back to plain text
            if os.path.exists(self.brain_path):
                with open(self.brain_path, 'r', encoding='utf-8') as f:
                    self._content = f.read()
            else:
                self._content = ""
        
        return self._content
    
    def search(self, query: str) -> list:
        """
        Search knowledge base for matching lines.
        
        Args:
            query: Search query
        
        Returns:
            List of matching lines
        """
        content = self.load()
        if not content:
            return []
        
        query_lower = query.lower()
        lines = content.split('\n')
        matching = [line for line in lines if query_lower in line.lower() and line.strip()]
        return matching
    
    def save(self, content: str, encrypt: bool = True) -> bool:
        """
        Save content to knowledge base.
        
        Args:
            content: Content to save
            encrypt: Whether to encrypt (default True)
        
        Returns:
            Success boolean
        """
        try:
            if encrypt:
                password = self._get_password()
                encrypt_file_content = encrypt_content(content, password)
                with open(self.encrypted_path, 'wb') as f:
                    f.write(encrypt_file_content)
                self._is_encrypted = True
            else:
                with open(self.brain_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            self._content = content
            return True
        except Exception as e:
            print(Fore.RED + f"✗ Error saving knowledge base: {e}")
            return False


# Quick test
if __name__ == "__main__":
    print("Testing encryption module...")
    
    # Test encrypt/decrypt roundtrip
    test_content = "My WiFi password is 'SuperSecret123'"
    test_password = "testpassword"
    
    encrypted = encrypt_content(test_content, test_password)
    print(f"Encrypted: {encrypted[:50]}...")
    
    decrypted = decrypt_content(encrypted, test_password)
    print(f"Decrypted: {decrypted}")
    
    assert decrypted == test_content, "Roundtrip failed!"
    print(Fore.GREEN + "✓ Encryption test passed!")
