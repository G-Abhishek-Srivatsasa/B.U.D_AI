import time
import sys

def log(msg):
    print(f"[{time.time() - start_time:.2f}s] {msg}")

start_time = time.time()
print("--- BEGIN PROFILING ---")

log("Importing standard libs...")
import threading
import requests
import random
import os

log("Importing modules.vision_server (includes cv2 & flask)...")
from modules import vision_server

log("Importing modules.brain (includes langchain & ollama)...")
from modules import brain

log("Importing modules.speak...")
from modules import speak

log("Importing modules.listen (includes speech_recognition)...")
from modules import listen

log("Importing modules.skills...")
from modules import skills

log("Importing modules.internet...")
from modules import internet

log("Importing modules.mail...")
from modules import mail

try:
    log("Importing pygetwindow...")
    import pygetwindow as gw
except ImportError:
    log("pygetwindow not found")

log("Imports finished.")

# Mocking parts of main.py to test logic speed without full execution
def mock_start():
    log("Mocking start_bud...")
    
    log("Starting Vision Server thread...")
    server_thread = threading.Thread(target=vision_server.start_server)
    server_thread.daemon = True 
    server_thread.start()
    
    log("Sleeping for 3 seconds (as per main.py)...")
    time.sleep(3)
    
    log("Generating initial response (LLM)...")
    # We call the actual function to test LLM latency
    # Note: This might talk out loud if speak.speak works
    response = brain.think("Generate a short, cool, natural 1-sentence spoken response (no special chars) for this situation: Initializing security protocols")
    log(f"LLM Response generated: {response}")
    
    log("Simulating speak (skipping actual audio to avoid noise if possible, but calling logic)...")
    # We won't call speak.speak to avoid annoying the user, just measure generation
    
    log("Checking verification status (1 attempt)...")
    try:
        response = requests.get('http://127.0.0.1:5000/check_status')
        log(f"Verification status: {response.status_code}")
    except Exception as e:
        log(f"Verification check failed (expected if server not ready): {e}")

    log("--- PROFILING COMPLETE ---")

if __name__ == "__main__":
    mock_start()
