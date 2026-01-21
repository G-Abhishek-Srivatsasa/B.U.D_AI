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
        "chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        "google chrome": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
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
        "discord": "discord.exe", # Works if Discord is in your PATH
        "youtube": "start https://www.youtube.com", # Quick fix for "Open YouTube"
        "whatsapp": "start whatsapp:" # Opens Desktop App
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

try:
    import pywhatkit as kit
except Exception as e:
    print(f"Warning: pywhatkit not found or offline ({e}). Using browser fallback.")
    kit = None

def play_youtube(topic):
    """
    Searches and plays a topic on YouTube using PyWhatKit.
    Returns True if successful, False otherwise.
    """
    print(f">> EXECUTING: PLAYING {topic}")
    try:
        if kit:
            kit.playonyt(topic)
            return True
        else:
            raise ImportError("PyWhatKit missing")
    except Exception as e:
        print(f"PyWhatKit error: {e}. Falling back to browser.")
        try:
            query = topic.replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={query}"
            webbrowser.open(url)
            return True
        except:
            return False

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

def get_clipboard_content():
    """ 
    Retrieves text from the clipboard. 
    Tries multiple methods for robustness.
    """
    print(">> EXECUTING: READING CLIPBOARD")
    
    # Method 1: Pyperclip (if available) - preferred because it's clean
    try:
        import pyperclip
        return pyperclip.paste()
    except ImportError:
        pass

    # Method 2: Tkinter (Common in standard libs)
    try:
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        content = root.clipboard_get()
        root.destroy()
        return content
    except:
        pass
        
    # Method 3: PowerShell (Universal Windows Fallback)
    try:
        # Get-Clipboard is built into PowerShell 5.0+ (Windows 10/11 default)
        cmd = "powershell Get-Clipboard"
        result = subprocess.check_output(cmd, shell=True).decode('utf-8').strip()
        return result 
    except Exception as e:
        print(f"Clipboard Error: {e}")
        return ""

# ... (Keep all your existing imports and functions) ...

# --- FILE SYSTEM OPERATIONS (Global Access) ---

# Define the Safe Zone (Default / Fallback)
WORKSPACE = os.path.join(os.getcwd(), 'workspace')
if not os.path.exists(WORKSPACE):
    os.makedirs(WORKSPACE)

def resolve_path(filename):
    """
    Intelligently resolves the path.
    1. If 'filename' is an absolute path (e.g. C:/Users/...), use it.
    2. If it's just a filename (e.g. note.txt), put it in the WORKSPACE.
    """
    # Check if it has a drive letter or root slash
    if os.path.isabs(filename):
        return filename
    else:
        return os.path.join(WORKSPACE, filename)

def is_safe_to_delete(path):
    """
    Prevents BUD from deleting critical system files.
    Returns True if safe, False if dangerous.
    """
    path = os.path.abspath(path).lower()
    
    # Critical System Paths to PROTECT
    forbidden_prefixes = [
        os.path.abspath(os.environ.get('SystemRoot', 'C:\\Windows')).lower(),
        os.path.abspath(os.environ.get('ProgramFiles', 'C:\\Program Files')).lower(),
        os.path.abspath(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')).lower(),
        os.path.abspath(os.path.join(os.environ.get('SystemRoot', 'C:\\Windows'), 'System32')).lower()
    ]

    # Prevent deleting the ROOT of the drive (C:\)
    if len(path) <= 3 and path.endswith(":\\"):
        return False
        
    # Check if the path is inside a forbidden area
    for forbidden in forbidden_prefixes:
        if path.startswith(forbidden):
            return False
            
    return True

def create_file(filename, content=""):
    """ Creates a new file (Global Access). """
    path = resolve_path(filename)
    try:
        # Ensure directory exists if it's a nested path
        folder = os.path.dirname(path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)
            
        with open(path, 'w') as f:
            f.write(content)
        print(f">> FILE SUCCESS: Created {path}")
        return True
    except Exception as e:
        print(f"Error creating file: {e}")
        return False

def append_to_file(filename, content):
    """ Adds text to the end of an existing file (Global Access). """
    path = resolve_path(filename)
    if not os.path.exists(path):
        print("Error: File does not exist.")
        return False
    try:
        with open(path, 'a') as f:
            f.write("\n" + content)
        print(f">> FILE SUCCESS: Appended to {path}")
        return True
    except Exception as e:
        print(f"Error appending file: {e}")
        return False

def read_file(filename):
    """ Reads the content of a file (Global Access). """
    path = resolve_path(filename)
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return None
    try:
        with open(path, 'r') as f:
            return f.read()
    except Exception as e:
        print(f"Error reading file: {e}")
        return None

def delete_file(filename):
    """ Deletes a file (With Safety Checks). """
    path = resolve_path(filename)
    
    # 1. Safety Check
    if not is_safe_to_delete(path):
        print(f">> SECURITY ALERT: Prevented deletion of system file: {path}")
        return False

    # 2. Delete
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f">> FILE SUCCESS: Deleted {path}")
            return True
        except Exception as e:
            print(f"Error deleting file: {e}")
            return False
    else:
        print("Error: File not found.")
        return False

import json
import os

# ... (keep your existing functions) ...

MEMORY_FILE = "long_term_memory.json"

def remember(key, value):
    """Saves a fact to a permanent JSON file."""
    data = {}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
        except:
            data = {}

    data[key.lower().strip()] = value.strip()
    
    with open(MEMORY_FILE, 'w') as f:
        json.dump(data, f, indent=4)

def recall(key):
    """Retrieves a fact from the JSON file."""
    if not os.path.exists(MEMORY_FILE):
        return None
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            # Exact match
            if key.lower() in data:
                return data[key.lower()]
            # Fuzzy search (e.g. asking for "wifi" finds "wifi password")
            for k, v in data.items():
                if key.lower() in k:
                    return v
            return None
    except:
        return None

# --- AUTONOMOUS MEMORY EXPANSION ---

def log_activity(activity):
    """
    Logs what the user is doing to the long-term memory file.
    Example: "User is coding in Visual Studio Code"
    """
    try:
        # Load existing data
        data = {}
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, 'r') as f:
                data = json.load(f)
        
        # Ensure 'activity_log' list exists
        if "activity_log" not in data:
            data["activity_log"] = []
            
        # Create new entry with timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {activity}"
        
        # Add to log (Keep distinct, avoid duplicates in a row)
        if not data["activity_log"] or activity not in data["activity_log"][-1]:
             data["activity_log"].append(entry)
             
        # Keep log size manageable (last 50 items)
        if len(data["activity_log"]) > 50:
            data["activity_log"] = data["activity_log"][-50:]
            
        # Save back
        with open(MEMORY_FILE, 'w') as f:
            json.dump(data, f, indent=4)
            
    except Exception as e:
        print(f"Memory Log Error: {e}")

def get_recent_context():
    """
    Returns the last 3 activities to give B.U.D context.
    """
    if not os.path.exists(MEMORY_FILE):
        return "No recent activity recorded."
        
    try:
        with open(MEMORY_FILE, 'r') as f:
            data = json.load(f)
            
        if "activity_log" in data and data["activity_log"]:
            return "; ".join(data["activity_log"][-3:])
        else:
            return "No recent activity recorded."
    except:
        return "Error reading memory."

# --- WHATSAPP AUTOMATION (GHOST MODE) ---

def send_whatsapp_desktop(target_name, message):
    """
    Automates the WhatsApp Desktop App to send a message.
    """
    print(f">> EXECUTING: WHATSAPP TO {target_name}")
    
    # 1. Resolve Contact Name
    real_name = target_name
    contacts_file = "contacts.json"
    
    if os.path.exists(contacts_file):
        try:
            with open(contacts_file, 'r') as f:
                contacts = json.load(f)
            if target_name.lower() in contacts:
                real_name = contacts[target_name.lower()]
                print(f"   [CONTACT] Mapped '{target_name}' -> '{real_name}'")
        except:
            pass

    # 2. Automation Sequence
    try:
        # Open App
        os.system("start whatsapp:")
        time.sleep(2.5) # Wait for app to open
        
        # New Chat (Ctrl + N)
        pyautogui.hotkey('ctrl', 'n')
        time.sleep(1)
        
        # Search Contact
        pyautogui.write(real_name)
        time.sleep(1.5) # Wait for search results
        
        # Select (Enter)
        pyautogui.press('enter')
        time.sleep(1)
        
        # Type Message
        pyautogui.write(message)
        time.sleep(0.5)
        
        # Send (Enter)
        pyautogui.press('enter')
        print(">> MESSAGE SENT SUCCESSFULLY")
        return True
        
    except Exception as e:
        print(f"WhatsApp Error: {e}")
        return False