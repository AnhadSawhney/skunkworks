#import machine_email
import settings
import transactions
import animatedGIF as ag
from sys import platform
import time
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
import io

VALVE_OPEN_TIME = 10
NUM_PIXELS = 24
FPS = 15
FRAMETIME = 1 / FPS
emulate = False
idle = True # volatile

#font = ImageFont.truetype("DejaVuSans.ttf", 24)

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

if is_raspberrypi():
    import board
    import neopixel
    import digitalio
    from adafruit_rgb_display.rgb import color565
    from adafruit_rgb_display import st7789
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS)


    # Configuration for CS and DC pins for Raspberry Pi
    cs_pin = digitalio.DigitalInOut(board.CE0)
    dc_pin = digitalio.DigitalInOut(board.D25)
    reset_pin = None
    BAUDRATE = 64000000  # The pi can be very fast!
    # Create the ST7789 display:
    display = st7789.ST7789(
        board.SPI(),
        cs=cs_pin,
        dc=dc_pin,
        rst=reset_pin,
        baudrate=BAUDRATE,
        width=135,
        height=240,
        x_offset=53,
        y_offset=40,
    )

    backlight = digitalio.DigitalInOut(board.D22)
    backlight.switch_to_output()
    backlight.value = True
    buttonA = digitalio.DigitalInOut(board.D23)
    buttonB = digitalio.DigitalInOut(board.D24)
    buttonA.switch_to_input()
    buttonB.switch_to_input()
else:
    #import tkinter as tk
    #root = tk.Tk()
    #root.withdraw()
    import neopixelEmulator as ne
    pixels = ne.Neopixel_Emulator(NUM_PIXELS)
    import displayEmulator as de
    display = de.DisplayEmulator()
    emulate = True

logo = ag.AnimatedGif(display)

def check_for_drink():
    

def start_idle():
    global idle
    idle = True
    t = Thread(target=idle_animation)
    t.start()
    return

def stop_idle():
    global idle
    idle = False
    t.join()
    return

def idle_animation():
    j = 0
    while idle:
        start = time.monotonic()
        #print("Idle Animation Loop")
        for i in range(NUM_PIXELS):
            pixel_index = (i * 256 // NUM_PIXELS) + j
            pixels.setPixelColor(i, wheel(pixel_index & 255))
        pixels.show()
        logo.postFrame()
        j += 2
        if j > 255:
            j = 0

        s = time.monotonic() - start
        if s < FRAMETIME:
            time.sleep(FRAMETIME - s)
        else:
            print("Frame time overloaded")

def dispense_drink():
    open_valve()
    for i in range(256): #change to number of LEDs in ring
        # animation: fill in the ring less and less as time runs out and fade from green to red 
        pixels.fill((i, 255 - i, 0)) # r, g, b
        for i in range(i/255*NUM_PIXELS, NUM_PIXELS):
            pixels.setPixelColor(i, 0, 0, 0)
        pixels.show()
        time.sleep(VALVE_OPEN_TIME / 255)
    close_valve()

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        r = g = b = 0
    elif pos < 85:
        r = int(pos * 3)
        g = int(255 - pos * 3)
        b = 0
    elif pos < 170:
        pos -= 85
        r = int(255 - pos * 3)
        g = 0
        b = int(pos * 3)
    else:
        pos -= 170
        r = 0
        g = int(pos * 3)
        b = int(255 - pos * 3)
    return (r, g, b)

def open_valve():
    return

def close_valve():
    return

def main():
    display.begin()
    pixels.begin()
    logo.preload("out.gif")

    start_idle()

if __name__ == '__main__':
    main()

# if __name__ == '__main__':
#     display = de.DisplayEmulator()
#     display.begin()
#     logo = ag.AnimatedGif(display)
#     logo.preload("out.gif")

#     while True:
#         #print('loop')
#         logo.postFrame()
#         time.sleep(0.1)
