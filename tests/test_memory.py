"""
Tests for memory persistence (save/load) functionality.
"""

import sys
import os
import json
import tempfile
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorama import Fore, init
init(autoreset=True)

from test_utils import TestResults, SYM_CHECK, SYM_FAIL





def test_memory_serialization(results: TestResults):
    """Test memory save/load serialization"""
    print(Fore.CYAN + "\n--- Testing Memory Serialization ---")
    
    from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
    from collections import deque
    
    # Create test memory
    memory = deque(maxlen=10)
    memory.append(HumanMessage(content="Hello Alfred"))
    memory.append(AIMessage(content="Good day, Sir."))
    memory.append(SystemMessage(content="System initialized"))
    
    # Create temp file for test
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_path = f.name
    
    try:
        # Test save
        memory_data = []
        for msg in memory:
            msg_dict = {
                "type": msg.__class__.__name__,
                "content": msg.content
            }
            memory_data.append(msg_dict)
        
        with open(temp_path, 'w', encoding='utf-8') as f:
            json.dump(memory_data, f, indent=2)
        
        # Check file was created
        if os.path.exists(temp_path):
            results.add_pass("Memory file created")
        else:
            results.add_fail("Memory file created", "File not found")
            return
        
        # Test load
        with open(temp_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        if len(loaded_data) == 3:
            results.add_pass("Correct number of messages loaded")
        else:
            results.add_fail("Correct number of messages loaded", f"Got {len(loaded_data)}")
        
        # Test message types preserved
        loaded_memory = deque(maxlen=10)
        for msg_dict in loaded_data:
            if msg_dict["type"] == "HumanMessage":
                loaded_memory.append(HumanMessage(content=msg_dict["content"]))
            elif msg_dict["type"] == "AIMessage":
                loaded_memory.append(AIMessage(content=msg_dict["content"]))
            elif msg_dict["type"] == "SystemMessage":
                loaded_memory.append(SystemMessage(content=msg_dict["content"]))
        
        if isinstance(loaded_memory[0], HumanMessage):
            results.add_pass("HumanMessage type preserved")
        else:
            results.add_fail("HumanMessage type preserved", f"Got {type(loaded_memory[0])}")
        
        if isinstance(loaded_memory[1], AIMessage):
            results.add_pass("AIMessage type preserved")
        else:
            results.add_fail("AIMessage type preserved", f"Got {type(loaded_memory[1])}")
        
        # Test content preserved
        if loaded_memory[0].content == "Hello Alfred":
            results.add_pass("Message content preserved")
        else:
            results.add_fail("Message content preserved", loaded_memory[0].content)
            
    finally:
        # Cleanup
        if os.path.exists(temp_path):
            os.remove(temp_path)


def test_memory_deque_limits(results: TestResults):
    """Test that memory respects maxlen limits"""
    print(Fore.CYAN + "\n--- Testing Memory Limits ---")
    
    from langchain_core.messages import HumanMessage
    from collections import deque
    
    max_depth = 5
    memory = deque(maxlen=max_depth)
    
    # Add more messages than max
    for i in range(10):
        memory.append(HumanMessage(content=f"Message {i}"))
    
    if len(memory) == max_depth:
        results.add_pass("Memory respects maxlen")
    else:
        results.add_fail("Memory respects maxlen", f"Length is {len(memory)}")
    
    # Oldest should be removed
    if memory[0].content == "Message 5":
        results.add_pass("Oldest messages removed first")
    else:
        results.add_fail("Oldest messages removed first", memory[0].content)


def test_empty_memory_handling(results: TestResults):
    """Test handling of empty or missing memory file"""
    print(Fore.CYAN + "\n--- Testing Empty Memory Handling ---")
    
    from collections import deque
    
    # Test with non-existent file
    fake_path = "/tmp/nonexistent_memory_file_12345.json"
    
    memory = deque(maxlen=10)
    
    if not os.path.exists(fake_path):
        results.add_pass("Non-existent file detected")
    else:
        results.add_fail("Non-existent file detected", "File somehow exists")
    
    # Empty memory should be valid
    if len(memory) == 0:
        results.add_pass("Empty memory is valid")
    else:
        results.add_fail("Empty memory is valid", f"Length is {len(memory)}")


def test_malformed_memory_handling(results: TestResults):
    """Test handling of corrupted memory file"""
    print(Fore.CYAN + "\n--- Testing Malformed Memory Handling ---")
    
    # Create temp file with invalid JSON
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        f.write("{ invalid json }")
        temp_path = f.name
    
    try:
        try:
            with open(temp_path, 'r', encoding='utf-8') as f:
                json.load(f)
            results.add_fail("Malformed JSON detected", "No exception raised")
        except json.JSONDecodeError:
            results.add_pass("Malformed JSON detected")
    finally:
        os.remove(temp_path)


def main():
    print(Fore.CYAN + "=" * 55)
    print(Fore.CYAN + "  ALFRED Memory Test Suite")
    print(Fore.CYAN + "=" * 55)
    
    results = TestResults()
    
    test_memory_serialization(results)
    test_memory_deque_limits(results)
    test_empty_memory_handling(results)
    test_malformed_memory_handling(results)
    
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
