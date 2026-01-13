import asyncio
import edge_tts
import pygame
import os

# Voice Selection: 'en-US-ChristopherNeural' is a great male voice.
# You can swap this for 'en-US-AriaNeural' if you prefer a female voice.
VOICE = "en-GB-RyanNeural"
BUFFER_FILE = "bud_speech.mp3"

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
        pygame.mixer.init()
        pygame.mixer.music.load(BUFFER_FILE)
        pygame.mixer.music.play()

        # Keep the program running while the audio plays
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

    except Exception as e:
        print(f"Error playing audio: {e}")
    
    finally:
        # 3. Cleanup: Stop the mixer and delete the temp file
        pygame.mixer.quit()
        if os.path.exists(BUFFER_FILE):
            try:
                os.remove(BUFFER_FILE)
            except PermissionError:
                pass # Sometimes Windows holds the file for a split second longer

if __name__ == "__main__":
    print("Testing B.U.D.'s voice...")
    speak("I didn't say you stole my money")