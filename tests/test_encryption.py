"""
Tests for the encryption module.
"""

import sys
import os
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorama import Fore, init
init(autoreset=True)

from test_utils import TestResults, SYM_CHECK, SYM_FAIL





def test_encrypt_decrypt_roundtrip(results: TestResults):
    """Test that encryption and decryption work correctly"""
    print(Fore.CYAN + "\n--- Testing Encrypt/Decrypt Roundtrip ---")
    
    from core.encryption import encrypt_content, decrypt_content
    
    test_cases = [
        ("Simple text", "password123"),
        ("My WiFi password is 'SuperSecret'", "strongpass"),
        ("Multi\nline\ncontent", "pass"),
        ("Special chars: !@#$%^&*()", "p@ssw0rd!"),
        ("Unicode: 你好世界 🌍", "unicode_pass"),
    ]
    
    for content, password in test_cases:
        try:
            encrypted = encrypt_content(content, password)
            decrypted = decrypt_content(encrypted, password)
            
            if decrypted == content:
                # Use repr() to safely print unicode content
                safe_content = repr(content)
                if len(safe_content) > 25:
                    safe_content = safe_content[:20] + "..." + safe_content[-1]
                results.add_pass(f"Roundtrip: {safe_content}")
            else:
                safe_content = repr(content)
                results.add_fail(f"Roundtrip: {safe_content}", "Content mismatch")
        except Exception as e:
            safe_content = repr(content)
            results.add_fail(f"Roundtrip: {safe_content}", str(e))


def test_wrong_password(results: TestResults):
    """Test that wrong password raises error"""
    print(Fore.CYAN + "\n--- Testing Wrong Password ---")
    
    from core.encryption import encrypt_content, decrypt_content
    from cryptography.fernet import InvalidToken
    
    content = "Secret data"
    correct_password = "correct_password"
    wrong_password = "wrong_password"
    
    encrypted = encrypt_content(content, correct_password)
    
    try:
        decrypt_content(encrypted, wrong_password)
        results.add_fail("Wrong password rejected", "No exception raised")
    except InvalidToken:
        results.add_pass("Wrong password rejected (InvalidToken)")
    except Exception as e:
        results.add_fail("Wrong password rejected", f"Unexpected error: {e}")


def test_file_encryption(results: TestResults):
    """Test file encryption and decryption"""
    print(Fore.CYAN + "\n--- Testing File Encryption ---")
    
    from core.encryption import encrypt_file, decrypt_file
    
    test_content = "This is my personal knowledge base.\nMy WiFi password is 'TestPass123'."
    password = "file_password"
    
    # Create temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        plain_path = f.name
    
    encrypted_path = plain_path + '.enc'
    
    try:
        # Encrypt
        result_path = encrypt_file(plain_path, password, encrypted_path)
        
        if os.path.exists(result_path):
            results.add_pass("Encrypted file created")
        else:
            results.add_fail("Encrypted file created", "File not found")
            return
        
        # Check encrypted file is different
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        if test_content.encode() not in encrypted_data:
            results.add_pass("Content is encrypted (not plaintext)")
        else:
            results.add_fail("Content is encrypted", "Plaintext found in encrypted file")
        
        # Decrypt
        decrypted = decrypt_file(encrypted_path, password)
        
        if decrypted == test_content:
            results.add_pass("File decryption successful")
        else:
            results.add_fail("File decryption successful", "Content mismatch")
            
    finally:
        # Cleanup
        if os.path.exists(plain_path):
            os.remove(plain_path)
        if os.path.exists(encrypted_path):
            os.remove(encrypted_path)


def test_secure_knowledge_base(results: TestResults):
    """Test SecureKnowledgeBase class"""
    print(Fore.CYAN + "\n--- Testing SecureKnowledgeBase ---")
    
    from core.encryption import SecureKnowledgeBase, encrypt_file
    
    test_content = "My name is Test User.\nMy favorite color is blue.\nMy WiFi is 'TestWiFi'."
    password = "kb_password"
    
    # Create temp files
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write(test_content)
        plain_path = f.name
    
    try:
        # Test with plain text file
        kb = SecureKnowledgeBase(plain_path, password=password)
        content = kb.load()
        
        if content == test_content:
            results.add_pass("Load plain text file")
        else:
            results.add_fail("Load plain text file", "Content mismatch")
        
        # Test search
        matches = kb.search("name")
        if any("name" in m.lower() for m in matches):
            results.add_pass("Search finds matches")
        else:
            results.add_fail("Search finds matches", f"Got {matches}")
        
        # Test search with no results
        matches = kb.search("nonexistent123")
        if len(matches) == 0:
            results.add_pass("Search returns empty for no match")
        else:
            results.add_fail("Search returns empty for no match", f"Got {len(matches)} matches")
        
        # Test with encrypted file
        encrypted_path = plain_path + '.enc'
        encrypt_file(plain_path, password, encrypted_path)
        
        kb_enc = SecureKnowledgeBase(plain_path, password=password)
        kb_enc._is_encrypted = True  # Force encrypted mode
        kb_enc._content = None  # Reset cache
        
        content = kb_enc.load()
        if content == test_content:
            results.add_pass("Load encrypted file")
        else:
            results.add_fail("Load encrypted file", "Content mismatch")
            
    finally:
        if os.path.exists(plain_path):
            os.remove(plain_path)
        if os.path.exists(plain_path + '.enc'):
            os.remove(plain_path + '.enc')


def test_key_derivation_consistency(results: TestResults):
    """Test that same password always derives same key"""
    print(Fore.CYAN + "\n--- Testing Key Derivation Consistency ---")
    
    from core.encryption import derive_key
    
    password = "consistent_password"
    
    key1 = derive_key(password)
    key2 = derive_key(password)
    
    if key1 == key2:
        results.add_pass("Same password produces same key")
    else:
        results.add_fail("Same password produces same key", "Keys differ")
    
    # Different passwords should produce different keys
    key3 = derive_key("different_password")
    
    if key1 != key3:
        results.add_pass("Different passwords produce different keys")
    else:
        results.add_fail("Different passwords produce different keys", "Keys match")


def main():
    print(Fore.CYAN + "=" * 55)
    print(Fore.CYAN + "  ALFRED Encryption Test Suite")
    print(Fore.CYAN + "=" * 55)
    
    results = TestResults()
    
    test_encrypt_decrypt_roundtrip(results)
    test_wrong_password(results)
    test_file_encryption(results)
    test_secure_knowledge_base(results)
    test_key_derivation_consistency(results)
    
    # Summary
    print(Fore.CYAN + "\n" + "=" * 55)
    print(Fore.CYAN + "  TEST SUMMARY")
    print(Fore.CYAN + "=" * 55)
    
    total = results.passed + results.failed
    print(f"\n  Total Tests: {total}")
    print(Fore.GREEN + f"  Passed: {results.passed}")
    print(Fore.RED + f"  Failed: {results.failed}")
    
    if results.failed == 0:
        print(Fore.GREEN + f"\n  {SYM_CHECK} ALL TESTS PASSED!")
        return 0
    else:
        print(Fore.RED + f"\n  {SYM_FAIL} {results.failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
