import pyttsx3

engine = pyttsx3.init()

def voice_navigation(natural_instructions):
    print("\n🔊 Voice Navigation:")
    for instruction in natural_instructions:
        if instruction.strip():
            print(f"🎙️ Speaking: {instruction.strip()}")
            engine.say(instruction.strip())
            engine.runAndWait()
    engine.stop() # Properly stop the engine