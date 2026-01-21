import sys
import os
import time

# Add modules to path
sys.path.append(r"e:\ABHI\PYTHON\PYTHON--CORE-JOSE PORTILLA\PYHON PROJ\B.U.D")

from modules import brain, skills

def test_intent_classification():
    print("\n--- Testing Intent Classification ---")
    phrases = [
        "what is wrong in this code",
        "debug this code",
        "fix my code",
        "analyze this code for errors"
    ]
    
    passed = True
    for p in phrases:
        intents = brain.classify_intent(p)
        if "DEBUG_CODE" in intents:
            print(f"[PASS] '{p}' -> {intents}")
        else:
            print(f"[FAIL] '{p}' -> {intents}")
            passed = False
            
    if passed:
        print(">> Intent Classification Tests Passed")
    else:
        print(">> Intent Classification Tests Failed")

def test_clipboard_access():
    print("\n--- Testing Clipboard Access ---")
    test_str = "print('Hello World')"
    
    # Try to set clipboard via PowerShell for the test
    # Use -Value explicitly and proper escaping
    cmd = f'powershell -Command "Set-Clipboard -Value \'{test_str}\'"'
    os.system(cmd)
    time.sleep(2) # Give it more time
    
    content = skills.get_clipboard_content()
    print(f"Expected: {test_str}")
    print(f"Got:      {content}")
    
    if test_str in content:
        print("[PASS] Clipboard Read Successfully")
    else:
        print("[FAIL] Clipboard Read Failed")

if __name__ == "__main__":
    test_intent_classification()
    test_clipboard_access()
