import os
import ctypes
import webbrowser
import subprocess
import time
import pyautogui
import keyboard

# --- FAIL SAFE ---
# If the mouse moves to the top-left corner, the script stops.
pyautogui.FAILSAFE = True 

def lock_pc():
    """
    Instantly locks the Windows workstation.
    """
    print(">> EXECUTING: LOCK DOWN PROTOCOL")
    ctypes.windll.user32.LockWorkStation()

def open_website(url):
    """
    Opens a website in the default browser.
    """
    if not url.startswith('http'):
        url = 'https://' + url
    print(f">> EXECUTING: OPENING {url}")
    webbrowser.open(url)

def open_app(app_name):
    """
    Smart App Launcher:
    1. Checks a dictionary for 'nicknames' (e.g., 'word' -> 'winword').
    2. If not found, tries to run the command directly via Windows Shell.
    """
    # 1. Clean the input: "open google chrome" -> "google chrome"
    clean_name = app_name.replace("open", "").replace("launch", "").strip().lower()
    
    # 2. The Nickname List (Map what YOU say to what WINDOWS needs)
    app_map = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "chrome.exe",
        "google chrome": "chrome.exe",
        "code": "code.exe",  # VS Code
        "vscode": "code.exe",
        "command prompt": "cmd.exe",
        "cmd": "cmd.exe",
        "terminal": "wt.exe",       # Windows Terminal
        "word": "winword.exe",      # MS Word
        "excel": "excel.exe",       # MS Excel
        "powerpoint": "powerpnt.exe", # MS PowerPoint
        "spotify": "spotify.exe",
        "files": "explorer.exe",    # File Explorer
        "explorer": "explorer.exe",
        "edge": "msedge.exe",
        "settings": "start ms-settings:",
        "task manager": "taskmgr.exe",
        "discord": "discord.exe" # Works if Discord is in your PATH
    }

    # 3. Determine the command
    if clean_name in app_map:
        command = app_map[clean_name]
    else:
        # Fallback: Try to run exactly what the user said
        command = clean_name

    print(f">> EXECUTING: LAUNCHING {command}")

    try:
        # shell=True allows Windows to search the system PATH for the app
        subprocess.Popen(command, shell=True)
        return True
    except Exception as e:
        print(f"Could not launch {clean_name}: {e}")
        return False

def play_youtube(topic):
    """
    Searches and plays a topic on YouTube.
    """
    print(f">> EXECUTING: PLAYING {topic}")
    query = topic.replace(" ", "+")
    url = f"https://www.youtube.com/results?search_query={query}"
    webbrowser.open(url)

# --- ADVANCED SYSTEM CONTROLS (Using PyAutoGUI) ---

def minimize_all():
    """ Minimizes all windows to show desktop (Win + D) """
    print(">> EXECUTING: MINIMIZE ALL")
    pyautogui.hotkey('win', 'd')

def take_screenshot():
    """ Takes and saves a screenshot """
    print(">> EXECUTING: SCREENSHOT")
    filename = f"screenshot_{int(time.time())}.png"
    pyautogui.screenshot(filename)
    print(f"Saved {filename}")

def type_text(text):
    """ Dictation Mode: Types whatever you say """
    print(f">> EXECUTING: TYPING '{text}'")
    pyautogui.write(text, interval=0.05)

def close_window():
    """ Closes the active window (Alt + F4) """
    print(">> EXECUTING: CLOSE WINDOW")
    pyautogui.hotkey('alt', 'f4')

# ... (Keep all your existing imports and functions) ...

# --- FILE SYSTEM OPERATIONS (The Secretary Mode) ---

# Define the Safe Zone
WORKSPACE = os.path.join(os.getcwd(), 'workspace')
if not os.path.exists(WORKSPACE):
    os.makedirs(WORKSPACE)

def create_file(filename, content=""):
    """ Creates a new file in the workspace. """
    path = os.path.join(WORKSPACE, filename)
    try:
        with open(path, 'w') as f:
            f.write(content)
        print(f">> FILE SUCCESS: Created {filename}")
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False

def append_to_file(filename, content):
    """ Adds text to the end of an existing file. """
    path = os.path.join(WORKSPACE, filename)
    if not os.path.exists(path):
        print("Error: File does not exist.")
        return False
    try:
        with open(path, 'a') as f:
            f.write("\n" + content)
        print(f">> FILE SUCCESS: Appended to {filename}")
        return True
    except Exception as e:
        print(f"Error appending file: {e}")
        return False

def read_file(filename):
    """ Reads the content of a file. """
    path = os.path.join(WORKSPACE, filename)
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def delete_file(filename):
    """ Deletes a file from the workspace. """
    path = os.path.join(WORKSPACE, filename)
    if os.path.exists(path):
        os.remove(path)
        print(f">> FILE SUCCESS: Deleted {filename}")
        return True
    else:
        print("Error: File not found.")
        return False