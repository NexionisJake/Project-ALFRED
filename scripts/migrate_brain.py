#!/usr/bin/env python3
"""
Migration script to encrypt existing brain.txt knowledge base.
Run this once to convert plain text to encrypted format.
"""

import sys
import os
import getpass

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorama import Fore, init
from core.encryption import encrypt_file, decrypt_file

init(autoreset=True)

def main():
    print(Fore.CYAN + "=" * 50)
    print(Fore.CYAN + "  ALFRED Knowledge Base Migration Tool")
    print(Fore.CYAN + "=" * 50)
    print()
    
    # Paths
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    brain_path = os.path.join(project_root, "data", "brain.txt")
    encrypted_path = brain_path + ".enc"
    
    # Check if brain.txt exists
    if not os.path.exists(brain_path):
        print(Fore.RED + f"✗ brain.txt not found at: {brain_path}")
        print(Fore.YELLOW + "  Create a brain.txt file first with your personal information.")
        return 1
    
    # Check if already encrypted
    if os.path.exists(encrypted_path):
        print(Fore.YELLOW + f"⚠ Encrypted file already exists: {encrypted_path}")
        response = input(Fore.WHITE + "  Overwrite? (y/n): ").strip().lower()
        if response != 'y':
            print(Fore.CYAN + "Migration cancelled.")
            return 0
    
    # Show current content
    print(Fore.WHITE + "\nCurrent brain.txt contents:")
    print(Fore.LIGHTBLACK_EX + "-" * 40)
    with open(brain_path, 'r', encoding='utf-8') as f:
        content = f.read()
        # Show first 500 chars
        preview = content[:500] + ("..." if len(content) > 500 else "")
        print(Fore.LIGHTBLACK_EX + preview)
    print(Fore.LIGHTBLACK_EX + "-" * 40)
    print()
    
    # Get password
    print(Fore.YELLOW + "Choose a strong password for encryption.")
    print(Fore.YELLOW + "You'll need this password every time ALFRED accesses your knowledge base.")
    print(Fore.YELLOW + "TIP: Set ALFRED_BRAIN_PASSWORD in .env to avoid repeated prompts.\n")
    
    password = getpass.getpass(Fore.WHITE + "Enter new password: ")
    password_confirm = getpass.getpass(Fore.WHITE + "Confirm password: ")
    
    if password != password_confirm:
        print(Fore.RED + "✗ Passwords do not match!")
        return 1
    
    if len(password) < 8:
        print(Fore.RED + "✗ Password must be at least 8 characters!")
        return 1
    
    # Encrypt
    try:
        output_path = encrypt_file(brain_path, password, encrypted_path)
        print(Fore.GREEN + f"\n✓ Successfully encrypted to: {output_path}")
        
        # Verify by decrypting
        print(Fore.CYAN + "  Verifying encryption...")
        decrypted = decrypt_file(encrypted_path, password)
        
        if decrypted == content:
            print(Fore.GREEN + "✓ Verification passed - encryption is working correctly!")
        else:
            print(Fore.RED + "✗ Verification failed - content mismatch!")
            return 1
        
        # Ask about removing original
        print()
        print(Fore.YELLOW + "⚠ SECURITY RECOMMENDATION:")
        print(Fore.YELLOW + "  The original brain.txt still contains your unencrypted data.")
        remove = input(Fore.WHITE + "  Delete original brain.txt? (y/n): ").strip().lower()
        
        if remove == 'y':
            os.remove(brain_path)
            print(Fore.GREEN + "✓ Original brain.txt deleted.")
        else:
            print(Fore.CYAN + "  Original file kept. Consider deleting it manually for security.")
        
        # Remind about .env
        print()
        print(Fore.CYAN + "=" * 50)
        print(Fore.GREEN + "  Migration Complete!")
        print(Fore.CYAN + "=" * 50)
        print()
        print(Fore.WHITE + "To avoid password prompts, add to your .env file:")
        print(Fore.YELLOW + f'  ALFRED_BRAIN_PASSWORD="{password}"')
        print()
        
        return 0
        
    except Exception as e:
        print(Fore.RED + f"✗ Encryption failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
