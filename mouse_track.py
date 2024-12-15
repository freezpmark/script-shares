import mouseinfo
mouseinfo.mouseInfo()


import threading
import time

import pyttsx3
from pynput import keyboard, mouse

# Global variable to track whether Ctrl key is pressed
ctrl_pressed = False
output_file = "clicks_log.txt"
instruction_voice_lines = [
    "Click on the plus button on the top right.",
    "Click on the student set.",
    "Click on the + load button on the left.",
    "Press ctrl+v, and then click on Load on the right.",
    "Click on any flash card's text field.",
    "Click on language selection. And do not move after it.",
    "Type the target language and press enter. Then, click on the second language selection.",
    "Type the target language and press enter. Then, click on create on the top right."
]
# Counter for the number of clicks
click_count = 0

# Lock to ensure thread-safe access to the engine
engine_lock = threading.Lock()

def speak_sentence(sentence):
    global click_count
    local_click_count = click_count
    while click_count == local_click_count:
        with engine_lock:
            engine = pyttsx3.init()
            engine.say(sentence)
            engine.runAndWait()
            del(engine)
            time.sleep(5)

def on_click(x, y, button, pressed):
    global ctrl_pressed, click_count
    if pressed and ctrl_pressed:
        click_info = f'Mouse clicked at ({x}, {y}) with {button}\n'
        with open(output_file, 'a') as file:
            file.write(click_info)
        print(f'Click information recorded: {click_info.strip()}')

        # Check if there are more sentences to speak
        if click_count < len(instruction_voice_lines):
            sentence_to_speak = instruction_voice_lines[click_count]
            threading.Thread(target=speak_sentence, args=(sentence_to_speak,)).start()
            click_count += 1
        else:
            print("All sentences spoken. Click recording complete.")
            return False

def on_key_event(key, is_press):
    global ctrl_pressed
    try:
        if key == keyboard.Key.ctrl_l:
            ctrl_pressed = is_press
            print(f'Ctrl {"pressed" if is_press else "released"}')
    except AttributeError:
        pass

def on_press(key):
    on_key_event(key, is_press=True)

def on_release(key):
    on_key_event(key, is_press=False)
    if key == keyboard.Key.esc:
        return False

# Collect events until released
with mouse.Listener(on_click=on_click) as listener1, keyboard.Listener(on_press=on_press, on_release=on_release) as listener2:
    listener1.join()
    listener2.join()
