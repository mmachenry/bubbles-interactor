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

outputs = [
    # mode 0
    [
        "fly",
        "fall",
        "jump",
        "Tell everyone three\nthings you're\nscared of.",
    ],
    # mode 1
    [
        "swim",
        "sail",
        "scuba dive",
        "drown",
    ],
    # mode 2
    [
        "dig",
        "spelunk",
        "bury",
        "tunnel",
    ],
]

colors = [(255,0,0), (0,255,0), (0,0,255)]

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
            text_area.text = random.choice(outputs[self.mode])
    
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
