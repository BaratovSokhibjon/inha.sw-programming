from gtts import gTTS
import pygame
import time

def clean_instruction(text):
    return text.replace("**", "").strip()

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

        tts = gTTS(text=clean_text, lang='en')
        tts.save("temp.mp3")

        play_audio("temp.mp3")