#!/usr/bin/env python3
"""
Master test runner for ALFRED.
Runs all test suites and provides a unified summary report.
"""

import sys
import os
import subprocess
import time

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from colorama import Fore, init
init(autoreset=True)

from test_utils import (SYM_CHECK, SYM_FAIL, SYM_WARN, SYM_PLAY, SYM_CHART, 
                        SYM_BOX_H, SYM_BOX_V, SYM_PARTY, SAFE_MODE)


def run_test_file(test_file: str, test_name: str) -> tuple:
    """
    Run a test file and capture results.
    
    Returns:
        (success: bool, output: str, duration: float)
    """
    start_time = time.time()
    
    # Force UTF-8 encoding for subprocess to avoid crashes when printing unicode
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    env["PYTHONUTF8"] = "1"
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            encoding='utf-8',  # Explicitly read as UTF-8
            errors='replace',  # Handle bad chars gracefully
            timeout=120,  # 2 minute timeout per test suite
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            env=env
        )
        
        duration = time.time() - start_time
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        return (success, output, duration)
        
    except subprocess.TimeoutExpired:
        return (False, "TIMEOUT: Test took too long", time.time() - start_time)
    except Exception as e:
        return (False, f"ERROR: {str(e)}", time.time() - start_time)


def main():
    print(Fore.CYAN + "=" * 60)
    print(Fore.CYAN + "  🤵 ALFRED - Master Test Suite Runner")
    print(Fore.CYAN + "=" * 60)
    print()
    
    tests_dir = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(tests_dir)
    
    # Define test suites to run
    test_suites = [
        ("preflight_check.py", "Pre-Flight System Check"),
        ("test_all_tools.py", "All Tools Test Suite"),
        ("test_memory.py", "Memory Persistence Tests"),
        ("test_encryption.py", "Encryption Module Tests"),
        ("test_tools_security.py", "Security Tests"),
    ]
    
    results = []
    total_start = time.time()
    
    for test_file, test_name in test_suites:
        test_path = os.path.join(tests_dir, test_file)
        
        if not os.path.exists(test_path):
            print(Fore.YELLOW + f"{SYM_WARN} Skipping {test_name} - file not found")
            continue
        
        print(Fore.WHITE + f"\n{SYM_PLAY} Running: {test_name}")
        print(Fore.LIGHTBLACK_EX + "-" * 50)
        
        success, output, duration = run_test_file(test_path, test_name)
        
        results.append({
            "name": test_name,
            "file": test_file,
            "success": success,
            "duration": duration
        })
        
        # Show abbreviated output
        lines = output.strip().split('\n')
        # Show last 10 lines (usually the summary)
        for line in lines[-10:]:
            # Sanitize output for Windows console if needed
            if SAFE_MODE:
                try:
                    line.encode(sys.stdout.encoding)
                except UnicodeEncodeError:
                    line = line.encode(sys.stdout.encoding, errors='replace').decode(sys.stdout.encoding)
            
            print(Fore.LIGHTBLACK_EX + "  " + line)
        
        status = Fore.GREEN + "PASSED" if success else Fore.RED + "FAILED"
        print(f"\n  Status: {status} ({duration:.2f}s)")
    
    total_duration = time.time() - total_start
    
    # Summary
    print(Fore.CYAN + "\n" + "=" * 60)
    print(Fore.CYAN + f"  {SYM_CHART} FINAL TEST SUMMARY")
    print(Fore.CYAN + "=" * 60)
    
    passed = sum(1 for r in results if r["success"])
    failed = sum(1 for r in results if not r["success"])
    
    print(f"\n  Test Suites Run: {len(results)}")
    print(Fore.GREEN + f"  Passed: {passed}")
    print(Fore.RED + f"  Failed: {failed}")
    print(f"  Total Time: {total_duration:.2f}s")
    
    print(Fore.WHITE + "\n  Results by Suite:")
    for r in results:
        status = Fore.GREEN + SYM_CHECK if r["success"] else Fore.RED + SYM_FAIL
        print(f"    {status} {r['name']} ({r['duration']:.2f}s)")
    
    if failed == 0:
        box_line = SYM_BOX_H * 35
        print(Fore.GREEN + f"\n  {box_line}")
        print(Fore.GREEN + f"  {SYM_BOX_V}   {SYM_PARTY} ALL TEST SUITES PASSED!   {SYM_BOX_V}")
        print(Fore.GREEN + f"  {box_line}")
        return 0
    else:
        print(Fore.RED + f"\n  {SYM_WARN} {failed} test suite(s) failed")
        print(Fore.YELLOW + "  Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
