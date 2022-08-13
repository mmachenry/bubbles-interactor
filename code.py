import time
import board
import terminalio
import neopixel
import digitalio
import asyncio
import keypad
import touchio
from displayio import Group
from adafruit_display_text import bitmap_label
from adafruit_lc709203f import LC709203F

outputs = [
    "run",
    "play",
    "hug",
    "hide",
    ]

output = ""

text_area = bitmap_label.Label(terminalio.FONT, scale=2)
text_area.anchor_point = (0.5, 0.5)
text_area.anchored_position = (board.DISPLAY.width // 2, board.DISPLAY.height // 2)

main_group = Group()
main_group.append(text_area)

touch = touchio.TouchIn(board.A5)

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
    with keypad.Keys((board.BUTTON,), value_when_pressed=False) as keys:
        while True:
            event = keys.events.get()
            if event:
                if event.pressed:
                    mode.next()
                    pixel.fill(colors[mode.value])
                #elif event.released:
                #    pass
            await asyncio.sleep(0)

async def capacitive_touch_rising_edge():
    while True:
        if touch.value:
            output = random.choice(outputs)
        await asyncio.sleep(0)

async def show_battery ():
    while True:
        text_area.text = output + "Battery:\n{:.1f} Volts \n{}%".format(sensor.cell_voltage, sensor.cell_percent)
        await asyncio.sleep(1.0)

async def main ():
    display_task = asyncio.create_task(show_battery())
    button_task = asyncio.create_task(button_rising_edge())
    touch_task = asyncio.create_task(capacitive_touch_rising_edge())
    await asyncio.gather(display_task, button_task, touch_task)

asyncio.run(main())
