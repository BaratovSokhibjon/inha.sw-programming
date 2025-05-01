from gtts import gTTS
import os
import hashlib
import pygame
import time

def clean_instruction(text):
    return text.replace("**", "").strip()

def text_to_filename(text):
    """Generate a consistent filename hash for a given instruction."""
    return "cache_" + hashlib.md5(text.encode()).hexdigest() + ".mp3"

def play_audio(filename):
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def voice_navigation(instructions):
    for instruction in instructions:
        if not instruction.strip():
            continue

        clean_text = clean_instruction(instruction)
        # print(f"🎙️ Speaking: {clean_text}")
        filename = text_to_filename(clean_text)

       
        if not os.path.exists(filename):
            tts = gTTS(text=clean_text, lang='en')
            tts.save(filename)

        play_audio(filename)