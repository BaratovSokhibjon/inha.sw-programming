from gtts import gTTS
import pygame
import time
from io import BytesIO


def clean_instruction(text):
    return text.replace("**", "").strip()

def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def voice_navigation(instructions):
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
    for instruction in instructions:
        if not instruction.strip():
            continue

        clean_text = clean_instruction(instruction)
        # print(f"🎙️ Speaking: {clean_text}")

        tts = gTTS(text=clean_text, lang='en')
        audio_data = BytesIO()
        tts.write_to_fp(audio_data)
        audio_data.seek(0)

        pygame.mixer.init()
        pygame.mixer.music.load(audio_data, "mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
