import speech_recognition as sr 
def listen():

    r = sr.Recognizer()
    print("Listening..." , end="" , flush=True)
    with sr.Microphone() as source :
         
        r.pause_threshold= 1 
        r.adjust_for_ambient_noise(source)

        try:
            audio = r.listen(source,timeout=5,phrase_time_limit=10)
            print("\rRecognizing...",end="" , flush=True)
            query = r.recognize_google(audio,language="en-in")
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