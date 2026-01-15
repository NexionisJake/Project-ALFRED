import os
import glob
from colorama import Fore

class AppLauncher:
    """
    Dynamically scans Windows Start Menu folders to find installed applications.
    Allows opening apps by their shortcut names (e.g., "Chrome", "Spotify").
    """
    def __init__(self):
        self.app_index = {}
        self._scan_installed_apps()

    def _scan_installed_apps(self):
        """Scans common Start Menu paths for .lnk files."""
        print(Fore.YELLOW + "🔍 Indexing installed applications...")
        
        # Common Start Menu locations
        paths = [
            os.path.expandvars(r"%ProgramData%\Microsoft\Windows\Start Menu\Programs"),
            os.path.expandvars(r"%AppData%\Microsoft\Windows\Start Menu\Programs")
        ]
        
        count = 0
        for path in paths:
            if not os.path.exists(path):
                continue
                
            # Recursive search for .lnk files
            # Python 3.10+ supports root_dir in glob, but we'll use simple walk or recursive glob
            search_pattern = os.path.join(path, "**", "*.lnk")
            for filepath in glob.glob(search_pattern, recursive=True):
                filename = os.path.basename(filepath)
                name_key = filename.lower().replace(".lnk", "")
                
                # Store full path
                self.app_index[name_key] = filepath
                count += 1
                
        print(Fore.GREEN + f"✔ Indexed {count} applications.")

    def get_app_path(self, app_name):
        """
        Returns the path to the application shortcut if found.
        Performs fuzzy-ish matching (exact substring).
        """
        key = app_name.lower()
        
        # 1. Exact Match
        if key in self.app_index:
            return self.app_index[key]
        
        # 2. Substring Match (e.g. "code" -> "visual studio code")
        # Prefer exact word matches or starts_with
        matches = [path for name, path in self.app_index.items() if key in name]
        
        if matches:
            # Return the shortest match (usually the most direct one, e.g. "Word" vs "Wordpad")
            # Or just the first one
            return matches[0]
            
        return None

    def refresh(self):
        """Re-scans the Start Menu."""
        self.app_index = {}
        self._scan_installed_apps()
