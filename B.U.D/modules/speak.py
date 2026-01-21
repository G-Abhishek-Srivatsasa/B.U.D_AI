import asyncio
import edge_tts
import pygame
import os

# Voice Selection: 'en-US-ChristopherNeural' is a great male voice.
# You can swap this for 'en-US-AriaNeural' if you prefer a female voice.
VOICE = "en-US-ChristopherNeural"
# --- PATH SETUP ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
BUFFER_FILE = os.path.join(PROJECT_ROOT, "bud_speech.mp3")

# Init mixer once on load to save time
try:
    pygame.mixer.init()
except:
    pass

async def _generate_audio(text):
    """Helper function to fetch audio from Edge TTS"""
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(BUFFER_FILE)

def speak(text):
    """The main function to make B.U.D. talk"""
    
    # 1. Generate the audio file
    try:
        asyncio.run(_generate_audio(text))
    except Exception as e:
        print(f"Error generating audio: {e}")
        return

    # 2. Play the audio using Pygame
    try:
        # Mixer is already initialized globally
        pygame.mixer.music.load(BUFFER_FILE)
        pygame.mixer.music.play()

        # Keep the program running while the audio plays
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error playing audio: {e}")
    
    finally:
        # 3. Cleanup: Stop but DO NOT QUIT mixer (keep it hot)
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
        if os.path.exists(BUFFER_FILE):
            try:
                os.remove(BUFFER_FILE)
            except PermissionError:
                pass

if __name__ == "__main__":
    print("Testing B.U.D.'s voice...")
    speak("I didn't say you stole my money")