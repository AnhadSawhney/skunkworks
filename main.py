import machine_email as email
from settings import *
import transactions
import animatedGIF as ag
from sys import platform
import time
from threading import Thread
from PIL import Image, ImageDraw, ImageFont
import io

VALVE_OPEN_TIME = 20
NUM_PIXELS = 16
FPS = 15
FRAMETIME = 1 / FPS
idle = True # volatile
image = None
draw = None
FONTSIZE = 20
valve = None
emulate = False

font1 = ImageFont.truetype("Daydream.ttf", FONTSIZE-8)
font2 = ImageFont.truetype("Mario-Kart-DS.ttf", FONTSIZE)

def is_raspberrypi():
    try:
        with io.open('/sys/firmware/devicetree/base/model', 'r') as m:
            if 'raspberry pi' in m.read().lower(): return True
    except Exception: pass
    return False

def open_valve():
    print("Valve open")
    global valve
    if valve is not None:
        valve.value = True
    return

def close_valve():
    print("Valve closed")
    global valve
    if valve is not None:
        valve.value = False
    return

if is_raspberrypi():
    print("Initializing Raspberry Pi")
    import board
    import neopixel
    import digitalio
    from adafruit_rgb_display.rgb import color565
    from adafruit_rgb_display import st7789
    pixels = neopixel.NeoPixel(board.D21, NUM_PIXELS)


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

    valve = digitalio.DigitalInOut(board.D20)
    valve.switch_to_output()
    close_valve()
else:
    print("Initializing Emulation")
    import neopixelEmulator as ne
    pixels = ne.Neopixel_Emulator(NUM_PIXELS)
    import displayEmulator as de
    display = de.DisplayEmulator()
    display.begin()
    pixels.begin()
    emulate = True


logo = ag.AnimatedGif(display)
settings = Settings()
PRICE = settings.price

def show_purchase(venmo):
    draw.rectangle((0, 0, display.width, display.height), outline=0, fill=(0, 0, 0))
    y = 2
    x = 2
    msg = '@'+venmo["Actor"]
    draw.text((x, y), "paid", font=font2, fill="#15a815")
    bbox = font1.getbbox(msg)
    x = display.width - bbox[2] - 2
    draw.text((x, y), msg, font=font1, fill="#00FF00")
    y += bbox[3] + 4

    x = 2

    msg = '$'+str(venmo["Amount"])
    draw.text((x, y), "amount", font=font2, fill="#1586a8")
    bbox = font1.getbbox(msg)
    x = display.width - bbox[2] - 2
    draw.text((x, y), msg, font=font1, fill="#05c2fc")
    y += bbox[3] + 4

    x = 2

    draw.text((x, y), "LET THE DELICIOUS", font=font2, fill="#914401")
    y += FONTSIZE + 4
    draw.text((x, y), "ROOT BEER FLOW!", font=font2, fill="#914401")
    y += FONTSIZE + 4
    draw.text((x, y), "make sure to close", font=font2, fill="#3802fc")
    y += FONTSIZE + 4
    draw.text((x, y), "the tap completely!", font=font2, fill="#FF00FF")
    display.image(image)


def start_idle():
    global idle, t
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
            if emulate:
                pixels.setPixelColor(i, wheel(pixel_index & 255))
            else:
                pixels[i] = wheel(pixel_index & 255)
        pixels.show()
        logo.postFrame()
        j += 3
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
        for i in range(int((1-i/255)*NUM_PIXELS), NUM_PIXELS):
            if emulate:
                pixels.setPixelColor(i, (0, 0, 0))
            else:
                pixels[i] = (0, 0, 0)
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

def main():
    global image
    image = Image.new("RGB", (display.width, display.height))
    global draw
    draw = ImageDraw.Draw(image)

    logo.preload("out.gif")

    start_idle()
    while True:
        venmos = email.check_venmos()
        if len(venmos) > 0:
            stop_idle()
            for venmo in venmos:
                if venmo["amount"] == PRICE:
                    show_purchase(venmo)
                    transactions.add_transaction(venmo)
                    dispense_drink()
                    time.sleep(1)
            start_idle()

        time.sleep(1)
        

if __name__ == '__main__':
    main()
