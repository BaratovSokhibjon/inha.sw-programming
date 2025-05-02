import pyttsx3

engine = pyttsx3.init()

def voice_navigation(natural_instructions):
    """
    Provides functionality to navigate using voice guidance based on natural language
    instructions provided as input.

    This function uses a text-to-speech engine to speak each instruction aloud for
    the user. It processes a list of instructions, ensuring proper output and stopping
    the engine after completing all instructions.

    Parameters
    ----------
    natural_instructions : list of str
        A list of natural language instructions to be spoken aloud.

    """
    print("\n🔊 Voice Navigation:")
    for instruction in natural_instructions:
        if instruction.strip():
            print(f"🎙️ Speaking: {instruction.strip()}")
            engine.say(instruction.strip())
            engine.runAndWait()
    engine.stop() # Properly stop the engine
