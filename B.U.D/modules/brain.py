from langchain_ollama import OllamaLLM

model = OllamaLLM(model="llama3.2")

def think(prompt):
    """
    Normal Chat Mode: Allows creativity.
    """
    return model.invoke(prompt)

def classify_intent(user_text):
    """
    Classifies user intent into a strict COMMAND string.
    """
    system_instruction = f"""
    You are a command classifier. You do NOT write code.
    
    INPUT: "{user_text}"
    
    You must output EXACTLY ONE of the following text lines:
    
    - LOCK_PC
    - SLEEP
    - MINIMIZE
    - SCREENSHOT
    - OPEN_APP | [app_name]
    - SEARCH | [query]
    - CREATE_FILE | [filename]
    - DELETE_FILE | [filename]
    - TYPE | [text_content]
    - CHAT
    
    SPECIFIC RULES:
    1. **IMPORTANT**: You must base your output ONLY on the valid "INPUT" provided above. Do NOT use the examples below as output unless the input matches them exactly.
    
    2. **TYPE**: Extract the raw sentence exactly as spoken by the user after the word "type".
       - Input: "Type this is amazing" -> Output: TYPE | this is amazing
       - Input: "Type hello world" -> Output: TYPE | hello world
       
    3. **CREATE_FILE**: Extract strict filenames. Convert "dot" to ".".
       - Input: "Create hello dot c" -> Output: CREATE_FILE | hello.c
       
    4. **OPEN_APP**: Extract the app name.
       - Input: "Open notepad" -> Output: OPEN_APP | notepad
    
    RETURN ONLY THE COMMAND LINE. NO EXTRA TEXT.
    """
    
    # 1. Get Raw Output
    decision = model.invoke(system_instruction).strip()
    
    # 2. SAFETY CLEANER (Removes "Here is the code..." or markdown)
    if "```" in decision:
        decision = decision.replace("```python", "").replace("```", "").strip()
    
    # 3. Line cleaner
    lines = decision.split('\n')
    for line in lines:
        clean_line = line.strip().upper()
        if any(cmd in clean_line for cmd in ["LOCK", "SLEEP", "OPEN", "CREATE", "DELETE", "SEARCH", "TYPE", "CHAT", "MINIMIZE", "SCREENSHOT"]):
            # Return the clean version (removing quotes)
            return line.strip().replace('"', '').replace("'", "")

    return "CHAT"