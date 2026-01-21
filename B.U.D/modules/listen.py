import speech_recognition as sr 
def listen():

    r = sr.Recognizer()
    print("Listening..." , end="" , flush=True)
    with sr.Microphone() as source :
         
        # DYNAMIC ENERGY ADJUSTMENT
        r.dynamic_energy_threshold = True
        r.energy_threshold = 300  # Default starting value
        r.pause_threshold = 0.6   # Response speed: Fast (0.6s silence = end of speech)

        try:
            # Reduced timeout to 3s to allow loop to check for boredom more often
            audio = r.listen(source, timeout=3, phrase_time_limit=20)
            print("\rRecognizing...", end="" , flush=True)
            query = r.recognize_google(audio, language="en-in")
            print(f"You Said: {query}")

            return query

        except Exception as e:
            # CHANGE THIS to see the actual error
            print(f"\nError: {e}") 
            return None 

if __name__ == "__main__" :
    print("Testing Microphone...")
    while True :
        text = listen()
        if text :
            print(f"Final output: {text}")