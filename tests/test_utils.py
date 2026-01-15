import sys
from colorama import Fore, init

# Initialize colorama
init(autoreset=True)

# Detect if we need safe ASCII (Windows + non-UTF-8)
SAFE_MODE = sys.platform == 'win32' and sys.stdout.encoding.lower() not in ('utf-8', 'utf8')

if SAFE_MODE:
    SYM_CHECK = "[OK]"
    SYM_FAIL = "[X]"
    SYM_WARN = "(!)"
    SYM_PLAY = ">>"
    SYM_CHART = "#"
    SYM_SEP = "="
    SYM_BOX_H = "="
    SYM_BOX_V = "|"
    SYM_PARTY = "*"
else:
    SYM_CHECK = "✓"
    SYM_FAIL = "✗"
    SYM_WARN = "⚠"
    SYM_PLAY = "▶"
    SYM_CHART = "📊"
    SYM_SEP = "═"
    SYM_BOX_H = "═"
    SYM_BOX_V = "║"
    SYM_PARTY = "🎉"

def get_status_symbol(success: bool) -> str:
    return SYM_CHECK if success else SYM_FAIL

def get_status_color(success: bool) -> str:
    return Fore.GREEN if success else Fore.RED

class TestResults:
    """Track test results"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
    
    def add_pass(self, name):
        self.passed += 1
        print(Fore.GREEN + f"  {SYM_CHECK} {name}")
    
    def add_fail(self, name, reason):
        self.failed += 1
        self.errors.append((name, reason))
        print(Fore.RED + f"  {SYM_FAIL} {name}: {reason}")
