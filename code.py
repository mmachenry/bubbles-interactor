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

output = None

text_area = bitmap_label.Label(terminalio.FONT, scale=2)
text_area.anchor_point = (0.5, 0.5)
text_area.anchored_position = (board.DISPLAY.width // 2, board.DISPLAY.height // 2)

main_group = Group()
main_group.append(text_area)

touch = touchio.TouchIn(board.D5)

sensor = LC709203F(board.I2C())

board.DISPLAY.show(main_group)

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)

#led = digitalio.DigitalInOut(board.LED)
#led.direction = digitalio.Direction.OUTPUT

class Mode:
    def __init__ (self, num):
        self.value = 0
        self.num = num

    def next (self):
        self.value = (self.value + 1) % self.num

mode = Mode(3)

colors = [(255,0,0), (0,255,0), (0,0,255)]

async def button_rising_edge ():
    global output
    with keypad.Keys((board.BUTTON,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    if output:
                        output = None
                    else:
                        mode.next()
                        pixel.fill(colors[mode.value])
                #elif event.released:
                #    pass
            await asyncio.sleep(0)

async def capacitive_touch_rising_edge():
    global output
    while True:
        if touch.value:
            if not output:
                output = random.choice(outputs[mode.value])
        await asyncio.sleep(0)

def display_battery ():
    text_area.text = "Battery:\n{:.1f} Volts \n{}%".format(sensor.cell_voltage, sensor.cell_percent)
    time.sleep(1)

async def display_output ():
    while True:
        if output:
            text = output
        else:
            text = "Press for an\ninteraction"
        
        if text_area.text != text:
            text_area.text = text
        await asyncio.sleep(1)

async def main ():
    display_task = asyncio.create_task(display_output())
    button_task = asyncio.create_task(button_rising_edge())
    touch_task = asyncio.create_task(capacitive_touch_rising_edge())
    await asyncio.gather(display_task, button_task, touch_task)

display_battery()
pixel.fill(colors[mode.value])
asyncio.run(main())
