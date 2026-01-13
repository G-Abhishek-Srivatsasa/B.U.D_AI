import time
import webbrowser
import threading
import requests
import sys
import winsound
import os

# Import your modules
from modules import vision_server, brain, speak, listen, skills, internet

# --- CONFIGURATION ---
WAKE_WORDS = ["hey bud", "bud", "buddy", "wake up", "hello bud"]
SLEEP_WORDS = ["go to sleep", "sleep", "standby", "shut up", "stop listening", "quiet", "offline"]

def play_wake_sound():
    winsound.Beep(600, 100)
    winsound.Beep(1200, 100)

def generate_response(situation):
    """Asks the Brain for a short, natural response."""
    return brain.think(f"Generate a short, cool, natural 1-sentence spoken response (no special chars) for this situation: {situation}")

def get_ai_confirmation(action):
    """Asks the Brain for a short, cool confirmation phrase."""
    return generate_response(f"I just did this: {action}")

def start_bud():
    print("------------------------------------------")
    print(" B.U.D. (Binary User Daemon) is Online")
    print("------------------------------------------")
    
    # 1. Start Vision Server (The UI/Animation)
    print("   [SYSTEM] Starting Interface Server...")
    server_thread = threading.Thread(target=vision_server.start_server)
    server_thread.daemon = True 
    server_thread.start()
    
    # CRITICAL: Wait 3 seconds for the server to fully start
    time.sleep(3)
    
    # 2. FORCE OPEN CHROME
    # This URL matches your Flask server
    url = 'http://127.0.0.1:5000'
    
    # Common path for Chrome on Windows. 
    # If this doesn't work, check "Program Files (x86)"
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
    
    print("   [SYSTEM] Launching Security Interface...")
    try:
        # Try to use Chrome specifically
        webbrowser.get(chrome_path).open(url)
    except Exception as e:
        # Fallback to default browser if Chrome isn't found at that path
        print(f"   [WARN] Chrome not found at standard path. Using default browser. Error: {e}")
        webbrowser.open(url)

    speak.speak(generate_response("Initializing security protocols"))

    # 3. Wait for Face Verification
    verified = False
    start_time = time.time()
    while not verified:
        # TIMEOUT CHECK: If 3 minutes pass without verification, shut down (or ask for password - future feature)
        if time.time() - start_time > 180: 
            print("timeout waiting for verification")
            # For now, we just loop, but in production we should exit or fallback
            pass 

        if not server_thread.is_alive():
            print("[CRITICAL ERROR] Vision Server thread died. Exiting.")
            return

        try:
            response = requests.get('http://127.0.0.1:5000/check_status')
            if response.json()['verified']:
                verified = True
                print("\nACCESS GRANTED.")
                break
        except requests.exceptions.ConnectionError:
            # Server not up yet, ignore
            pass
        except Exception as e:
            print(f"Verification Error: {e}")
            
        time.sleep(1)

    # 4. Welcome User
    speak.speak(generate_response("Identity verified. Systems online."))
    is_awake = True 

    # --- MAIN LOOP ---
    while True:
        try:
            # --- MAIN LOOP LOGIC ---
            if is_awake:
                print("\n(ONLINE) Listening...", end="", flush=True)
            else:
                print("\n(STANDBY) Waiting for 'Hey Bud'...", end="", flush=True)
                
            user_input = listen.listen()
            
            if user_input is None:
                continue
    
            text = user_input.lower()
            print(f"\nYou said: {text}")
    
            # --- 1. SLEEPING LOGIC (Hardcoded for Speed) ---
            if not is_awake:
                for trigger in WAKE_WORDS:
                    if trigger in text:
                        is_awake = True
                        play_wake_sound()
                        speak.speak(generate_response("I have come online"))
                        break 
                if not is_awake: continue 
    
            # --- 2. AWAKE LOGIC ---
            if is_awake:
                
                # 🔴 PRIORITY 1: INSTANT SLEEP CHECK
                # We check this manually so he shuts up IMMEDIATELY.
                if any(word in text for word in SLEEP_WORDS):
                    speak.speak(generate_response("I am going offline/standby"))
                    is_awake = False
                    continue
    
                # 🟢 PRIORITY 2: ASK THE BRAIN
                print(f"   [THINKING] ...")
                intent_raw = brain.classify_intent(text)
                print(f"   [INTENT] {intent_raw}") 
                
                # Parse Command | Parameter
                if "|" in intent_raw:
                    parts = intent_raw.split("|", 1)
                    command = parts[0].strip().upper()
                    param = parts[1].strip()
                else:
                    command = intent_raw.strip().upper()
                    param = ""
    
                # --- EXECUTION BLOCK ---
                
                if command == "LOCK_PC":
                    speak.speak(generate_response("I am locking the system"))
                    skills.lock_pc()
                    # We break here because locking usually stops the script/user interaction
                    break 
                    
                elif command == "MINIMIZE":
                    skills.minimize_all()
                    
                elif command == "SCREENSHOT":
                    speak.speak(generate_response("Taking a screenshot"))
                    skills.take_screenshot()
    
                elif command == "SEARCH":
                    if param:
                        speak.speak(generate_response(f"Searching the web for {param}"))
                        result = internet.search_web(param)
                        # Ask Brain to summarize the search result
                        summary = brain.think(f"Summarize this search result in one sentence: {result}")
                        speak.speak(summary)
                    else:
                        speak.speak(generate_response("Ask the user what they want to search for"))
    
                elif command == "OPEN_APP":
                    # Fix common AI typos
                    if "calc" in param.lower(): param = "calculator"
                    speak.speak(generate_response(f"Opening {param}"))
                    skills.open_app(param)
    
                elif command == "CREATE_FILE":
                    if param:
                        speak.speak(generate_response(f"Creating file {param}, ask what to write inside"))
                        content = listen.listen()
                        
                        if content:
                            skills.create_file(param, content)
                            speak.speak(generate_response(f"File {param} has been saved"))
                        else:
                            # TIMEOUT FIX: Don't create empty files if silence
                            speak.speak(generate_response("I didn't hear input so cancelled file creation"))
                    else:
                        speak.speak(generate_response("Ask user for the file name"))
                
                elif command == "DELETE_FILE":
                    if param:
                        speak.speak(generate_response(f"Deleting file {param}"))
                        skills.delete_file(param)
                    else:
                        speak.speak(generate_response("Ask which file to delete"))
    
                elif command == "TYPE":
                    if param:
                        speak.speak(generate_response("I am typing the text now"))
                        skills.type_text(param)
    
                else:
                    # Chat fallback (For greetings, jokes, etc.)
                    response = brain.think(user_input)
                    speak.speak(response)

        except KeyboardInterrupt:
            print("\nShutting down B.U.D...")
            break
        except Exception as e:
            print(f"\n[CRITICAL ERROR in Main Loop]: {e}")
            speak.speak("I encountered a critical error. Please check the console.")
            # Retry loop instead of crashing
            time.sleep(2)
            continue

if __name__ == "__main__":
    start_bud()