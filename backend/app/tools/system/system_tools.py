import subprocess
import shutil
from langchain.tools import tool

@tool
def open_system_app(app_name: str) -> str:
    """
    Opens a system application on the user's Linux PC. 
    Pass the common command name of the application (e.g. 'firefox', 'gnome-calculator', 'code', 'spotify', 'thunderbird').
    """
    # Common mappings for user-friendly names to linux binary commands
    app_map = {
        "calculator": "gnome-calculator",
        "calc": "gnome-calculator",
        "browser": "firefox",
        "chrome": "google-chrome",
        "vscode": "code",
        "terminal": "gnome-terminal",
        "files": "nautilus",
        "explorer": "nautilus",
        "settings": "gnome-control-center",
        "text editor": "gedit"
    }
    
    command = app_map.get(app_name.lower(), app_name.lower())
    
    # Check if the binary exists in the system PATH
    if not shutil.which(command):
        return f"Error: Application '{command}' not found on the system."
        
    try:
        # Popen starts the process in the background without blocking the FastAPI server
        subprocess.Popen([command], start_new_session=True)
        return f"Successfully opened {app_name} on the host PC."
    except Exception as e:
        return f"Failed to open {app_name}: {str(e)}"

import os

@tool
def list_installed_apps() -> str:
    """
    Lists common desktop applications installed on the user's Linux host PC.
    """
    try:
        apps = []
        # Check desktop files in standard linux directories
        paths = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for path in paths:
            if os.path.exists(path):
                for file in os.listdir(path):
                    if file.endswith(".desktop"):
                        # Clean up name for readability
                        app_name = file.replace(".desktop", "").replace("org.gnome.", "").replace("com.", "")
                        apps.append(app_name)
        
        if not apps:
            return "No desktop applications found."
            
        # Return unique sorted list
        unique_apps = sorted(list(set(apps)))
        return "Installed Applications:\n" + ", ".join(unique_apps[:60])
    except Exception as e:
        return f"Failed to list applications: {str(e)}"

@tool
def change_system_wallpaper(image_path: str) -> str:
    """
    Changes the desktop wallpaper on the user's Linux PC (GNOME desktop).
    Provide the absolute path to the image file (e.g. '/home/username/Pictures/wallpaper.jpg').
    """
    try:
        # Expand user ~ if present
        abs_path = os.path.abspath(os.path.expanduser(image_path))
        if not os.path.exists(abs_path):
            return f"Error: Image file not found at '{abs_path}'."
            
        # GNOME gsettings command to change wallpaper (supports both light and dark modes)
        cmd_light = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{abs_path}"]
        cmd_dark = ["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", f"file://{abs_path}"]
        
        subprocess.run(cmd_light, check=True)
        subprocess.run(cmd_dark, check=True)
        return f"Successfully changed desktop wallpaper to '{abs_path}'."
    except Exception as e:
        return f"Failed to change wallpaper: {str(e)}"
