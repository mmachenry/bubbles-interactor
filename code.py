import time
import board
import terminalio
import neopixel
import digitalio
import asyncio
import keypad
import touchio
import random
from displayio import Group
from adafruit_display_text import bitmap_label
from adafruit_lc709203f import LC709203F

mode_1 = [
    "What is the farthest sound you can hear?",
    "Pantomime something and i’ll guess what it is!",
    "Let’s try to harmonize a note.",
    "Give 3 compliments",
    "Describe a person you love",
    "Offer to hug someone creatively",
    "Share 3 interesting textures",
    "Describe something beautiful",
    "Sing a song",
    "Describe a wild experience",
    "Temporarily trade an item of clothing.",
    "Describe a pivotal time in your life",
    "Find 3 beautiful things to share with someone",
    "Describe something funny you’ve experienced",
    "Do a pole dance",
    "Pose like a famous art piece, and ask others to guess which",
    "Describe a favorite body part",
    "Tell a story without using words",
    "Do an interpretive dance on a theme",
    "Describe or show some of your greatest assets.",
    "Share something pleasant that requires a sense other than sight.",
    "Describe an unusual sensual experience that you love.",
    "Share a secret",
    "Describe a 'happy place.'",
    "Describe what makes you a freak.",
    "Describe an embarrassing moment.",
    "Improvise a poem.",
    "Describe how burning man influenced your life.",
    "Tell everyone three things you're scared of.",
]

mode_2 = [
    "Kiss me somewhere.",
    "Offer to kiss someone",
    "Offer someone a lap dance.",
    "Offer someone a massage",
    "Offer to gently caress someone’s face",
    "A Good Mutual Neck Sniff",
]

# Mode 0 is all of the modes lists together
outputs = [mode_1 + mode_2, mode_1, mode_2]
colors = [(255,0,0),(0,255,0), (0,0,255)]

# Initialize screen and display battery voltage for one second
text_area = bitmap_label.Label(terminalio.FONT, scale=2)
text_area.anchor_point = (0.5, 0.5)
text_area.anchored_position = (board.DISPLAY.width // 2, board.DISPLAY.height // 2)
main_group = Group()
main_group.append(text_area)
board.DISPLAY.show(main_group)
sensor = LC709203F(board.I2C())
text_area.text = "Battery:\n{:.1f} Volts \n{}%".format(sensor.cell_voltage, sensor.cell_percent)
time.sleep(1)

touch = touchio.TouchIn(board.D5)
pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

def default_word_wrap (sentence):
    words = sentence.split(" ")
    current_line_len = len(words[0])
    wrapped_sentence = words[0]
    for word in words[1:]:
        if len(word) + current_line_len > 19:
            wrapped_sentence += "\n"
            current_line_len = 0
        current_line_len += 1 + len(word)
        wrapped_sentence += " " + word
    return wrapped_sentence

class State:
    def __init__(self):
        self.displaying_interaction = False
        self.mode = 0
        self.num_modes = len(outputs)
        self._show_welcome_screen()
        self._indicate_mode()

    def mode_button(self):
        if self.displaying_interaction:
            self.displaying_interaction = False
            self._show_welcome_screen()
        else:
            self.mode = (self.mode + 1) % self.num_modes
            self._indicate_mode()

    def touch_button(self):
        if not self.displaying_interaction:
            self.displaying_interaction = True
            text_area.text = \
                default_word_wrap(
                    random.choice(outputs[self.mode]))
    
    def _show_welcome_screen(self):
        text_area.text = "Press for an\ninteraction"
        
    def _indicate_mode(self):
        pixel.fill(colors[self.mode])

state = State()

async def button_rising_edge ():
    global output
    with keypad.Keys((board.BUTTON,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    state.mode_button()
            await asyncio.sleep(0)

async def touch_rising_edge():
    global output
    while True:
        if touch.value:
            state.touch_button()
        await asyncio.sleep(0)

async def main ():
    button_task = asyncio.create_task(button_rising_edge())
    touch_task = asyncio.create_task(touch_rising_edge())
    await asyncio.gather(button_task, touch_task)

asyncio.run(main())
