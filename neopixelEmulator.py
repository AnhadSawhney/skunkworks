#!/usr/bin/env python3

#Import lines for dev build of pygame on Ubuntu (remove this pair of lines for raspberry pi)
#I added them so I could develop in Thonny on Ubuntu using the latested development build of 
#pygame, as the packaged version of pygame that Thonny offered did not detect the full set of
#features of the game controllers I was using.
import sys, math, time
#sys.path.append('/usr/local/lib/python3.5/dist-packages/pygame-1.9.4.dev0-py3.5-linux-i686.egg')

import tkinter as tk
import threading
#import pygame

def RGBtoHEX(rgb):
    """translates an rgb tuple of int to a tkinter friendly color code
    """
    r, g, b = rgb
    return f'#{r:02x}{g:02x}{b:02x}'


def RGBtoInt(red, green, blue, white = 0):
	"""Convert the provided red, green, blue color to a 24-bit color value.
	Each color component should be a value 0-255 where 0 is the lowest intensity
	and 255 is the highest intensity.
	"""
	return (white << 24) | (red << 16)| (green << 8) | blue

# convert a 24 bit rgbw color to rgb hex value
def InttoHEX(c):
    #print(hex(c))
    c = hex(c).replace('0x', '#')#[:-2] # for white
    while len(c) < 7:
        c = c[0:3] + '0' + c[3:] #pad

    return c

class mock():
    WS2811_STRIP_RGB = 1
    WS2811_STRIP_GRB = 2


ws = mock()

class Neopixel_Emulator(object):
    """ A Pygame based application class to emulate an array of neopixels.
        The interface is based on the Adafruit Neopixel library python class
        so your code written against the emulator should work with that library
        and real neopixel devices without changes.

    """
    
    def __init__(self, num, pin=0, freq_hz=800000, dma=5, invert=False,
                brightness=255, channel=0, strip_type=ws.WS2811_STRIP_RGB):
        """Class to represent a NeoPixel/WS281x LED display.  Num should be the
        number of pixels in the display, and pin should be the GPIO pin connected
        to the display signal line (must be a PWM pin like 18!).  Optional
        parameters are freq, the frequency of the display signal in hertz (default
        800khz), dma, the DMA channel to use (default 5), invert, a boolean
        specifying if the signal line should be inverted (default False), and
        channel, the PWM channel to use (defaults to 0).
        """
        
        #Store parameters
        self.brightness = brightness
        self.numLEDs = num
        
        #Set initial values
        self.initialized = True
        self.led_pos = []
        self.led_data = []
        self.height = 640
        self.width = 640
        self.keep_looping = True
        self.new_data = False

        self.initialiseLEDCircle()
        
    
    def initialiseLEDCircle(self):
        """ Set LED positions in a circle """
        #LEDsize = int( 20 / num ) + 10
        radius = int(self.numLEDs * 10)

        self.led_data = [(0,0,0) for i in range(self.numLEDs)]
        
        #Position LEDs in a circle
        for i in range(self.numLEDs):
            angleRad = math.pi - (i * 2 * math.pi / self.numLEDs )
            x = int( radius * math.sin( angleRad ) + self.width / 2 )
            y = int( radius * math.cos( angleRad ) + self.height / 2 )
            self.led_pos.append( [x,y] )
            #self.setPixelColorRGB(i, int(155 * i / self.numLEDs )+100,0,0)

    def loop(self):
        root = tk.Tk() #tk.Toplevel()
        root.title('Neopixels')
        root.geometry('{}x{}'.format(self.width, self.height))
    
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        canvas = tk.Canvas(root, height=self.height, width=self.width, bg='black')
        canvas.pack()
        self.show()

        print("Neopixel Emulator Loop Start!")
        while self.keep_looping:
            if self.new_data:
                self.new_data = False
                for i in range(self.numLEDs):
                    x = self.led_pos[i][0]
                    y = self.led_pos[i][1]
                    c = RGBtoHEX(self.led_data[i])
                    canvas.create_rectangle(x, y, x+20, y+20, fill=c)

            canvas.pack()
            root.update()

            time.sleep(0.05)
        
        root.destroy()

    def on_closing(self):
        self.keep_looping = False  
        #self.t.join() 

    def begin(self):
        """Initialize library, must be called once before other functions are
        called.
        """
        self.initialized = True   
        self.t = threading.Thread(target=self.loop)
        self.t.start()     

    def show(self):
        """Update the display with the data from the LED buffer."""
        if self.initialized:
            self.new_data = True
        else:
            #Throw error as begin method of class has not been called
            print("Error: Class begin method was not called")
        
        
    def setPixelColor(self, n, color):
        """Set LED at position n to the provided 24-bit color value (in RGB order).
        """
        #if type(color) == int:
        #    color = IntToRGB(color[0], color[1], color[2])
        self.led_data[n] = color

    # add a fill method to fill the entire led data list with the given color
    def fill(self, color):
        """Fill the whole LED display with the given color."""
        for i in range(len(self.led_data)):
            self.setPixelColor(i, color)

    def setPixelColorRGB(self, n, red, green, blue, white = 0):
        """Set LED at position n to the provided red, green, and blue color.
        Each color component should be a value from 0 to 255 (where 0 is the
        lowest intensity and 255 is the highest intensity).
        """
        self.setPixelColor(n, (red, green, blue, white))
        

    def setBrightness(self, brightness):
        """Scale each LED in the buffer by the provided brightness.  A brightness
        of 0 is the darkest and 255 is the brightest.
        """


    def getPixels(self):
        """Return an object which allows access to the LED display data as if 
        it were a sequence of 24-bit RGB values.
        """
        return self.led_data
    

    def numPixels(self):
        """Return the number of pixels in the display."""
        return ws.ws2811_channel_t_count_get(self.channel)

    def getPixelColor(self, n):
        """Get the 24-bit RGB color value for the LED at position n."""
        return self.led_data[n]


def main():
    
    # LED strip configuration:
    LED_COUNT      = 24      # Number of LED pixels.
    LED_PIN        = 18      # GPIO pin connected to the pixels (18 uses PWM!).
    #LED_PIN        = 10      # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
    LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
    LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
    LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
    LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)
    LED_CHANNEL    = 0       # set to '1' for GPIOs 13, 19, 41, 45 or 53
    LED_STRIP      = ws.WS2811_STRIP_GRB   # Strip type and colour ordering
    
    # Create NeoPixel object with appropriate configuration.
    strip = Neopixel_Emulator(LED_COUNT)
    
    # Intialize the library (must be called once before other functions).
    strip.begin()

    strip.fill(RGBtoInt(255,0,0))
    strip.show()

    # keepRunning = True
    # while keepRunning == True :
    #     for event in pygame.event.get(): # User did something
    #         if event.type == pygame.QUIT: # If user clicked close
    #             keepRunning = False # Flag that we are done so we exit this loop
    #     for i in range(20):
    #         strip.setPixelColor(0, (0,i*10,0))
    #         strip.show()
    #         time.sleep(0.1)
    #         #print('a')

        
    #pygame.quit()


if __name__ == '__main__':
    main()
