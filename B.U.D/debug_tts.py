import asyncio
import edge_tts
import pygame
import os

VOICE = "en-GB-RyanNeural"
BUFFER_FILE = "debug_audio.mp3"

async def _test_gen():
    print(f"[DEBUG] Starting edge_tts generation with voice {VOICE}...")
    try:
        communicate = edge_tts.Communicate("Testing audio generation.", VOICE)
        await communicate.save(BUFFER_FILE)
        print(f"[DEBUG] edge_tts save complete. File created: {os.path.exists(BUFFER_FILE)}")
    except Exception as e:
        print(f"[ERROR] edge_tts failed: {e}")

def debug_speak():
    # 1. Generate
    try:
        asyncio.run(_test_gen())
    except Exception as e:
         print(f"[ERROR] asyncio run failed: {e}")

    if not os.path.exists(BUFFER_FILE):
        print("[ERROR] Audio file was not created. Aborting playback.")
        return

    # 2. Play
    print(f"[DEBUG] Initializing Pygame mixer...")
    try:
        pygame.mixer.init()
        print("[DEBUG] Loading music...")
        pygame.mixer.music.load(BUFFER_FILE)
        print("[DEBUG] Playing music...")
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        print("[DEBUG] Playback finished.")
    except Exception as e:
        print(f"[ERROR] Pygame playback failed: {e}")
    finally:
        pygame.mixer.quit()
        try:
            os.remove(BUFFER_FILE)
            print("[DEBUG] Cleanup complete.")
        except:
            pass

if __name__ == "__main__":
    debug_speak()
