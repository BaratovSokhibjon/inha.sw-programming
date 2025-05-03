from gtts import gTTS
import pygame
import time
from io import BytesIO

def clean_instruction(text):
    return text.replace("**", "").strip()

def play_audio_from_text(text):

    pygame.mixer.init()
    tts = gTTS(text=text, lang='en')
    audio_buffer = BytesIO()
    tts.write_to_fp(audio_buffer)
    audio_buffer.seek(0) 
    
    pygame.mixer.music.load(audio_buffer)
    pygame.mixer.music.play()
    
    while pygame.mixer.music.get_busy():
        time.sleep(0.1)

def voice_navigation(instructions):
    for instruction in instructions:
        if not instruction.strip():
            continue

        clean_text = clean_instruction(instruction)
        play_audio_from_text(clean_text)