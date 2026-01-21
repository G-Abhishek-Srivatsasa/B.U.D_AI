import json
import os
from langchain_ollama import OllamaLLM
import re

# Explicitly use 127.0.0.1 to avoid Windows localhost/IPv6 issues
model = OllamaLLM(model="llama3.2", base_url="http://127.0.0.1:11434")

# --- CONVERSATIONAL STATE ---
conversation_history = []
MAX_HISTORY = 10  # Keep last 10 turns

def think(prompt):
    """
    Normal Chat Mode: Allows creativity.
    """
    return model.invoke(prompt)

def load_memory():
    """Loads user data to personalize the chat."""
    try:
        if os.path.exists("long_term_memory.json"):
            with open("long_term_memory.json", "r") as f:
                data = json.load(f)
                # Filter out the massive activity log for the system prompt
                summary = {k: v for k, v in data.items() if k != "activity_log"}
                return json.dumps(summary, indent=2)
    except:
        pass
    return "{}"

# --- 3. COMMUNICATION INTELLIGENCE ---
def log_promise(promise_text):
    """Saves a promise to memory."""
    try:
        data = {}
        if os.path.exists("long_term_memory.json"):
            with open("long_term_memory.json", "r") as f:
                data = json.load(f)
        
        if "pending_promises" not in data:
            data["pending_promises"] = []
            
        # Add timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        data["pending_promises"].append(f"[{timestamp}] {promise_text}")
        
        with open("long_term_memory.json", "w") as f:
            json.dump(data, f, indent=4)
    except:
        pass

def extract_promise(text):
    """Checks if user made a commitment."""
    # Simple keyword patterns
    text = text.lower()
    if "i will" in text or "i'll" in text or "remind me to" in text:
        # Avoid simple future tense statements that aren't promises?
        # For now, capture broadly.
        log_promise(text)
        return True
    return False

def detect_sentiment(text):
    """
    Adjusts the persona tone based on user input.
    Returns: (Sentiment Label, Persona Modifier)
    """
    text = text.lower()
    negative_words = ["sad", "tired", "bad day", "annoyed", "stressed", "angry", "hate", "depressed"]
    
    if any(word in text for word in negative_words):
        return "NEGATIVE", "The user is feeling down. Be supportive, gentle, and concise. Low energy."
        
    return "NEUTRAL", "Be casual, witty, and chill. High energy."

def chat(user_input, context=""):
    """
     conversational_chat: Maintains history and persona.
    """
    global conversation_history
    
    # 1. Analyze Input (Communication Awareness)
    extract_promise(user_input)
    sentiment, tone_instruction = detect_sentiment(user_input)
    
    # 2. Load Persistence
    user_facts = load_memory()
    
    # 3. Define Persona (Adaptive)
    system_persona = f"""
    You are B.U.D (Binary User Daemon).
    
    RELATIONSHIP:
    You are the user's BEST FRIEND. 
    Mood Instruction: {tone_instruction}
    
    - You know everything about the user. Here is what you know: {user_facts}
    - NEVER sound like a robot assistant. 
    
    CURRENT SITUATION:
    The user is currently: [{context}]
    
    HISTORY:
    Use this to keep the conversation flowing naturally.
    """
    
    # 4. Build Prompt
    history_text = "\n".join(conversation_history)
    full_prompt = f"{system_persona}\n\nCONVERSATION SO FAR:\n{history_text}\n\nUser: {user_input}\nB.U.D:"
    
    # 5. Generate Response
    response = model.invoke(full_prompt).strip()
    
    # 6. Update History
    conversation_history.append(f"User: {user_input}")
    conversation_history.append(f"B.U.D: {response}")
    
    # Keep history managed
    if len(conversation_history) > MAX_HISTORY * 2:
        conversation_history = conversation_history[-(MAX_HISTORY * 2):]
        
    return response

def classify_intent(user_text):
    """
    Hybrid Router: Checks for patterns FIRST (Instant), then asks AI (Smart).
    Returns a LIST of commands.
    """
    text = user_text.lower().strip()
    commands = []

    # --- ⚡ TURBO MODE (Instant Regex Checks) ---
    
    # 1. LOCK SYSTEM
    if "lock" in text and ("pc" in text or "computer" in text or "system" in text):
        commands.append("LOCK_PC")

    # 2. OPEN APP
    # Matches: "open [app]", "launch [app]", "start [app]"
    match_open = re.search(r'(?:open|launch|start)\s+(.*)', text)
    if match_open:
        app_name = match_open.group(1).strip()
        # Avoid capturing "command" or "file" as an app name
        if "command" not in app_name and "file" not in app_name:
            commands.append(f"OPEN_APP | {app_name}")

    # 3. SEARCH
    # Matches: "search for [query]", "google [query]"
    match_search = re.search(r'(?:search for|google|find)\s+(.*)', text)
    if match_search:
        query = match_search.group(1).strip()
        commands.append(f"SEARCH | {query}")

    # 4. SYSTEM COMMAND (God Mode)
    # Matches: "Run command [X]", "Execute [X]"
    match_cmd = re.search(r'(?:run command|execute|system)\s+(.*)', text)
    if match_cmd:
        cmd = match_cmd.group(1).strip()
        commands.append(f"SYSTEM_CMD | {cmd}")

    # 5. READ FILE
    # Matches: "Read file [X]", "Read [X]"
    match_read = re.search(r'(?:read file|read)\s+(.*)', text)
    if match_read:
        filename = match_read.group(1).strip()
        filename = filename.replace(" dot ", ".")
        commands.append(f"READ_FILE | {filename}")

    # 6. MEMORY - SAVE
    # Matches: "Remember that my [password] is [1234]" OR "Remember [password] is [1234]"
    match_save = re.search(r'remember (?:that )?(?:my )?(.+) is (.+)', text)
    if match_save:
        key = match_save.group(1).strip()
        value = match_save.group(2).strip()
        commands.append(f"REMEMBER | {key}||{value}")

    # 7. MEMORY - RECALL
    # Matches: "What is my [password]?", "What's my [password]?"
    match_ask = re.search(r"what(?:'s|\s+is)\s+(?:my|the)\s+(.+)", text)
    if match_ask and "time" not in text and "weather" not in text:
        key = match_ask.group(1).replace("?", "").strip()
        commands.append(f"RECALL | {key}")

    # 8. TYPE (Smart Extraction)
    # Matches: "Type [text]"
    match_type = re.search(r'(?:type|write|dictate)\s+(.*)', text)
    if match_type:
        content = match_type.group(1).strip()
        # Only treat as TYPE if it's not a file creation command
        if "file" not in text: 
            commands.append(f"TYPE | {content}")

    # 9. YOUTUBE PLAYBACK
    # Matches: "Play [X] on YouTube", "YouTube [X]"
    match_yt = re.search(r'(?:play|watch)\s+(.*)\s+on youtube', text)
    if not match_yt:
         match_yt = re.search(r'youtube\s+(.*)', text)
         
    if match_yt:
        topic = match_yt.group(1).strip()
        commands.append(f"PLAY_YOUTUBE | {topic}")

    if match_yt:
        topic = match_yt.group(1).strip()
        commands.append(f"PLAY_YOUTUBE | {topic}")

    # 10. WHATSAPP MESSAGE
    # Matches: "Message [Name] [Content]", "Tell [Name] [Content]"
    # We assume the name is the first word after the command.
    match_msg = re.search(r'(?:message|tell|text)\s+(\w+)\s+(.+)', text)
    if match_msg:
        target = match_msg.group(1).strip()
        msg_content = match_msg.group(2).strip()
        commands.append(f"SEND_WHATSAPP | {target}||{msg_content}")
        
    # 11. CHECK EMAIL
    if "email" in text and ("check" in text or "read" in text or "new" in text):
        commands.append("CHECK_EMAIL")

    # 12. DEBUG CODE
    # Matches: "debug this code", "fix this code", "what is wrong in this code", "analyze code"
    match_debug = re.search(r'(?:debug|fix|analyze|wrong.*in)\s+(?:this\s+)?code', text)
    if match_debug:
        commands.append("DEBUG_CODE")

    # --- IF TURBO FOUND SOMETHING, RETURN IT NOW ---
    if commands:
        return commands

    # --- ⚡ FAST CHAT CHECK (Optimization) ---
    # If we didn't match a Turbo command, check if we even need to ask the AI.
    # If the user isn't asking to create/delete files or sleep, it's just chat.
    
    command_keywords = ["create", "make", "delete", "remove", "sleep", "standby", "shut up", "offline"]
    
    # If no command keywords are present, skip the LLM and return CHAT immediately
    if not any(word in text for word in command_keywords):
        return ["CHAT"]

    # --- 🐢 SLOW MODE (AI Fallback) ---
    # Only runs if regex failed AND potential command keywords exist.
    
    system_instruction = f"""
    You are a Command Extractor.
    INPUT: "{user_text}"
    
    OPTIONS:
    - CREATE_FILE | [filename] (Rules: ONLY if user says "create", "make", "new file". "dot c" -> ".c")
    - DELETE_FILE | [filename] (Rules: ONLY if user says "delete", "remove")
    - SLEEP
    - CHAT
    
    IMPORTANT RULES:
    1. If the input is just defined conversation (e.g. "that is crazy", "cool", "yes", "no"), output CHAT.
    2. Do NOT hallucinate commands. If you are unsure, output CHAT.
    
    RETURN ONLY THE COMMAND LINE.
    """
    
    decision = model.invoke(system_instruction).strip()
    
    # Clean up output
    if "```" in decision: decision = decision.replace("```python", "").replace("```", "").strip()
    
    lines = decision.split('\n')
    for line in lines:
        clean_line = line.strip().upper()
        if any(cmd in clean_line for cmd in ["CREATE", "DELETE", "SLEEP", "CHAT"]):
            return [line.strip().replace('"', '').replace("'", "")]

    return ["CHAT"]