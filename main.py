#import machine_email
import settings
import transactions
from sys import platform
from time import sleep
from threading import Thread
from PIL import Image, ImageDraw, ImageFont

VALVE_OPEN_TIME = 10
NUM_PIXELS = 24

#font = ImageFont.truetype("DejaVuSans.ttf", 24)

if platform == 'linux':
    import board
    import neopixel
    import digitalio
    from adafruit_rgb_display.rgb import color565
    from adafruit_rgb_display import st7789
    pixels = neopixel.NeoPixel(board.D18, NUM_PIXELS)
else:
    import neopixelEmulator as ne
    pixels = ne.Neopixel_Emulator(NUM_PIXELS)
    pixels.begin()

def main():
    t = Thread(target=idle_animation)
    t.start()

def piTFT_setup():
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

# def test_display():
#     if buttonA.value and buttonB.value:
#         backlight.value = False  # turn off backlight
#     else:
#         backlight.value = True  # turn on backlight
#     if buttonB.value and not buttonA.value:  # just button A pressed
#         display.fill(color565(255, 0, 0))  # red
#     if buttonA.value and not buttonB.value:  # just button B pressed
#         display.fill(color565(0, 0, 255))  # blue
#     if not buttonA.value and not buttonB.value:  # none pressed
#         display.fill(color565(0, 255, 0))  # green

def idle_animation():
    while True:
        for j in range(255):
            for i in range(NUM_PIXELS):
                pixel_index = (i * 256 // NUM_PIXELS) + j
                pixels.setPixelColor(i, wheel(pixel_index & 255))
            pixels.show()
            sleep(0.03)

def dispense_drink():
    open_valve()
    for i in range(256): #change to number of LEDs in ring
        # animation: fill in the ring less and less as time runs out and fade from green to red 
        pixels.fill((i, 255 - i, 0)) # r, g, b
        for i in range(i/255*NUM_PIXELS, NUM_PIXELS):
            pixels.setPixelColor(i, (0,0,0))
        pixels.show()
        sleep(VALVE_OPEN_TIME / 255)
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

if __name__ == '__main__':
    main()
