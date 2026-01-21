import time
import webbrowser
import threading
import requests
import sys
import winsound
import os
import random

# Import your modules
# Import your modules
from modules import vision_server, brain, speak, listen, skills, internet, mail, conscious, analytics

try:
    import pygetwindow as gw 
except ImportError:
    print("Warning: pygetwindow not found. Passive observation disabled.")
    gw = None

# --- CONFIGURATION ---
WAKE_WORDS = ["hey bud", "bud", "buddy", "wake up", "hello bud"]
SLEEP_WORDS = ["go to sleep", "sleep", "standby", "shut up", "stop listening", "quiet", "offline"]

# --- EMAIL CREDENTIALS ---
EMAIL_USER = "gabhisheksrivatsasa@gmail.com"
EMAIL_PASS = "wwrq valp ehfk jmle" 

# --- SPONTANEITY SETTINGS ---
# Dynamic Timer: B.U.D will speak randomly between min and max seconds
# Dynamic Timer: B.U.D will speak randomly between min and max seconds
MIN_SILENCE_DURATION = 30   # 30 seconds
MAX_SILENCE_DURATION = 90   # 1.5 minutes

def play_wake_sound():
    winsound.Beep(600, 100)
    winsound.Beep(1200, 100)

def generate_response(situation):
    """Asks the Brain for a short, natural response."""
    return brain.think(f"Generate a short, cool, natural 1-sentence spoken response (no special chars) for this situation: {situation}")

def get_spontaneous_thought():
    """Generates a random thought based on what you are doing."""
    context = skills.get_recent_context()
    
    # 50% chance to talk about context, 50% chance to be random/philosophical
    if random.choice([True, False]):
        prompt = f"You are a best friend hanging out while the user works. The user has been doing this: [{context}]. Say something short (1 sentence) and casual about it. Do not be robotic."
    else:
        prompt = "You are a best friend. Say something short, random, and interesting (sci-fi, tech, or philosophical) to break the silence. 1 sentence max."
        
    return brain.think(prompt)

def start_bud():
    print("------------------------------------------")
    print(" B.U.D. (Binary User Daemon) is Online")
    print("------------------------------------------")
    
    # 1. Start Vision Server
    print("   [SYSTEM] Starting Interface Server...")
    server_thread = threading.Thread(target=vision_server.start_server)
    server_thread.daemon = True 
    server_thread.start()
    
    time.sleep(3)
    
    # 2. FORCE OPEN CHROME
    url = 'http://127.0.0.1:5000'
    chrome_path = "C:/Program Files/Google/Chrome/Application/chrome.exe %s"
    try:
        webbrowser.get(chrome_path).open(url)
    except:
        print("   [WARN] Chrome not found. Using default.")
        webbrowser.open(url)

    speak.speak(generate_response("Initializing security protocols"))

    # 3. Wait for Face Verification
    verified = False
    while not verified:
        try:
            response = requests.get('http://127.0.0.1:5000/check_status')
            if response.json()['verified']:
                verified = True
                print("\nACCESS GRANTED.")
                break
        except:
            pass
        time.sleep(1)

    speak.speak(generate_response("Identity verified. Systems online."))
    is_awake = True 
    
    # Track time for spontaneity
    last_interaction_time = time.time()
    next_spontaneous_speech = time.time() + random.randint(MIN_SILENCE_DURATION, MAX_SILENCE_DURATION)
    
    # Track time for observation (every 30s)
    last_observation_time = time.time()

    # --- MAIN LOOP ---
    while True:
        try:
            if is_awake:
                print("\n(ONLINE) Listening...", end="", flush=True)
            else:
                print("\n(STANDBY) Waiting...", end="", flush=True)
                
            # --- PASSIVE OBSERVATION (Background Task) ---
            if is_awake and (time.time() - last_observation_time > 30):
                last_observation_time = time.time()
                try:
                    if gw:
                        window = gw.getActiveWindow()
                        if window and window.title:
                            # Log what the user is doing
                            # e.g. "User is using: main.py - Visual Studio Code"
                            cleaned_title = window.title.strip()
                            if cleaned_title:
                                # We print less to keep terminal clean
                                # print(f"   [OBSERVING] {cleaned_title}") 
                                skills.log_activity(f"User is using: {cleaned_title}")
                except Exception as e:
                    pass

            user_input = listen.listen()
            
                    # --- 1. SILENCE HANDLER (FRIEND MODE) ---
            if user_input is None:
                if is_awake:
                    # Check if it's time to speak randomly
                    if time.time() > next_spontaneous_speech:
                        # CHECK: Should I interrupt?
                        if conscious.should_interrupt(conscious.PRIORITY_LOW):
                            print("\n[SPONTANEOUS] Breaking silence...")
                            
                            # 1. Proactive Suggestion (Habit Check)
                            context = skills.get_recent_context()
                            suggestion = analytics.get_proactive_suggestion(context)
                            
                            if suggestion:
                                speak.speak(suggestion)
                            else:
                                # 2. Random Thought
                                speak.speak(get_spontaneous_thought())
                            
                            # Reset timer for next time (Random interval)
                            last_interaction_time = time.time()
                            # TEST MODE: Faster intervals (10-30s) instead of minutes
                            next_spontaneous_speech = time.time() + random.randint(10, 30)
                            print(f"[DEBUG] Next thought in approx {int(next_spontaneous_speech - time.time())}s")
                        else:
                            # User is busy. Delay thought by 30 seconds.
                            # print("   [CONSCIOUS] User busy. Holding thought.")
                            next_spontaneous_speech = time.time() + 30
                        
                continue
            
            # User spoke -> Reset timer
            last_interaction_time = time.time()
            text = user_input.lower()
            print(f"\nYou said: {text}")
    
            # --- 2. SLEEP LOGIC ---
            if not is_awake:
                for trigger in WAKE_WORDS:
                    if trigger in text:
                        is_awake = True
                        play_wake_sound()
                        speak.speak(generate_response("I have come online"))
                        break 
                if not is_awake: continue 
    
            # --- 3. AWAKE LOGIC ---
            if is_awake:
                
                # SLEEP CHECK
                if any(word in text for word in SLEEP_WORDS):
                    speak.speak(generate_response("Going offline"))
                    is_awake = False
                    continue
    
                # GET COMMANDS FROM BRAIN
                print(f"   [THINKING] ...")
                intent_list = brain.classify_intent(text)
                
                for intent_raw in intent_list:
                    print(f"   [INTENT] {intent_raw}") 
                    
                    if "|" in intent_raw:
                        parts = intent_raw.split("|", 1)
                        command = parts[0].strip().upper()
                        param = parts[1].strip()
                    else:
                        command = intent_raw.strip().upper()
                        param = ""
        
                    # --- EXECUTION ---
                    
                    if command == "LOCK_PC":
                        # No return check needed, instant
                        speak.speak(generate_response("Locking system"))
                        skills.lock_pc()
                        break 
                        
                    elif command == "PLAY_YOUTUBE":
                        # Check logic: Try first, speak result
                        if skills.play_youtube(param):
                            speak.speak(generate_response(f"Playing {param} on YouTube"))
                        else:
                            speak.speak(f"I couldn't play {param}. Please check your connection.")

                    elif command == "SEND_WHATSAPP":
                        if "||" in param:
                            target, msg = param.split("||", 1)
                            speak.speak("Sending message...") # Status update before long action
                            if skills.send_whatsapp_desktop(target, msg):
                                speak.speak(generate_response(f"Message sent to {target}"))
                            else:
                                speak.speak(f"I failed to send the message to {target}.")
                        else:
                            speak.speak("Who should I message?")

                    elif command == "CHECK_EMAIL":
                        speak.speak("Checking your inbox...")
                        emails = mail.get_unread_emails(EMAIL_USER, EMAIL_PASS)
                        
                        if emails and "Error" not in emails[0]:
                            # Ask Brain to summarize
                            email_text = "\n".join(emails)
                            summary = brain.think(f"Here are my unread emails:\n{email_text}\n\nSummarize who they are from and what they are about in 2 sentences.")
                            speak.speak(summary)
                        else:
                            speak.speak("I couldn't access your emails. Please check your credentials.")

                    elif command == "MINIMIZE":
                        skills.minimize_all()
                        
                    elif command == "SCREENSHOT":
                        if skills.take_screenshot():
                            speak.speak(generate_response("Screenshot taken"))
                        else:
                            speak.speak("I failed to take a screenshot.")
        
                    elif command == "SEARCH":
                        if param:
                            speak.speak(generate_response(f"Searching for {param}"))
                            result = internet.search_web(param)
                            if result:
                                summary = brain.think(f"Summarize this search result in one sentence: {result}")
                                speak.speak(summary)
                            else:
                                speak.speak("I found no results.")
                        else:
                            speak.speak("What should I search for?")
        
                    elif command == "OPEN_APP":
                        if "calc" in param: param = "calculator"
                        
                        # TRY FIRST
                        if skills.open_app(param):
                            speak.speak(generate_response(f"Opening {param}"))
                        else:
                            speak.speak(f"I couldn't find {param} installed on this computer.")
        
                    elif command == "CREATE_FILE":
                        if param:
                            speak.speak(generate_response(f"Creating {param}, what content?"))
                            content = listen.listen()
                            if content:
                                if skills.create_file(param, content):
                                    speak.speak("File saved successfully.")
                                else:
                                    speak.speak("I couldn't create the file.")
                            else:
                                speak.speak("Cancelled.")
                        else:
                            speak.speak("Name the file?")
                    
                    elif command == "DELETE_FILE":
                        if skills.delete_file(param):
                            speak.speak(generate_response(f"Deleted {param}"))
                        else:
                            speak.speak(f"I couldn't delete {param}. It might not exist or be protected.")
        
                    elif command == "TYPE":
                        if param:
                            skills.type_text(param)
                            
                    elif command == "SYSTEM_CMD":
                        speak.speak(f"Executing command: {param}")
                        skills.run_terminal(param)
                        
                    elif command == "READ_FILE":
                        speak.speak(f"Reading {param}")
                        content = skills.read_file(param)
                        if content:
                            speak.speak(content)
                        else:
                            speak.speak(f"I couldn't read {param}.")
                        
                    elif command == "REMEMBER":
                        if "||" in param:
                            key, val = param.split("||", 1)
                            skills.remember(key, val)
                            speak.speak(generate_response(f"I will remember {key} is {val}"))
                            
                    elif command == "RECALL":
                        val = skills.recall(param)
                        if val:
                            speak.speak(f"Your {param} is {val}.")
                        else:
                            speak.speak(generate_response(f"I don't have information on {param}"))
        
                    elif command == "DEBUG_CODE":
                        # speak.speak(generate_response("Analyzing the code from your clipboard..."))
                        code_snippet = skills.get_clipboard_content()
                        
                        if not code_snippet or len(code_snippet.strip()) < 5:
                            speak.speak(generate_response("There is no code in your clipboard."))
                        else:
                            speak.speak(generate_response("Analyzing code..."))
                            print(f"\n[DEBUGGING CODE]:\n{code_snippet[:100]}...\n")
                            prompt = f"""
                            You are an Expert Multi-Language Code Debugger.
                            Identify the programming language.
                            Review the following code snippet and find the error.
                            
                            CODE:
                            {code_snippet}
                            
                            INSTRUCTIONS:
                            1. Be concise.
                            2. Tell me what is wrong.
                            3. Provide the corrected code.
                            """
                            response = brain.think(prompt)
                            
                            # Print detailed response for reading
                            print("\n" + "="*40)
                            print(" B.U.D DIAGNOSIS")
                            print("="*40)
                            print(response)
                            print("="*40 + "\n")
                            
                            # Speak short summary
                            summary = brain.think(f"Summarize this debugging advice in 1 short sentence to say out loud: {response}")
                            speak.speak(summary)

                    else:
                        # Chat fallback - Uses Memory & Persona
                        # INJECT CONTEXT: Let the brain know what's happening
                        context = skills.get_recent_context()
                        response = brain.chat(user_input, context)
                        speak.speak(response)
        
                    # Small delay between commands
                    time.sleep(1)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
            continue

if __name__ == "__main__":
    start_bud()