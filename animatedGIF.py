from PIL import Image, ImageOps
import os
import time
import displayEmulator

class Frame:
    def __init__(self, duration=0):
        self.duration = duration
        self.image = None

class AnimatedGif:
    def __init__(self, display, width=None, height=None, folder=None):
        self.framecount = 0
        #self.loop = 0
        self.index = 0
        self.duration = 0
        self.frames = []

        if width is not None:
            self.width = width
        else:
            self.width = display.width
        if height is not None:
            self.height = height
        else:
            self.height = display.height
        self.display = display

    def preload(self, file):
        image = Image.open(file)
        print("Loading {}...".format(file))
        if "duration" in image.info:
            self.duration = image.info["duration"]
        else:
            self.duration = 0
        if "loop" in image.info:
            self.loop = image.info["loop"]
        else:
            self.loop = 1
        self.framecount = image.n_frames
        self.frames.clear()
        for i in range(self.framecount):
            image.seek(i)
            # Create blank image for drawing.
            # Make sure to create image with mode 'RGB' for full color.
            frameobject = Frame(duration=self.duration)
            if "duration" in image.info:
                frameobject.duration = image.info["duration"]
            #frameobject.image = ImageOps.pad(  # pylint: disable=no-member
            #    image.convert("RGB"),
            #    (self.width, self.height),
            #    method=Image.Resampling.NEAREST,
            #    color=(0, 0, 0),
            #    centering=(0.5, 0.5),
            #)
            frameobject.image = image.copy() #image.convert("RGB")
            #frameobject.image.show()
            self.frames.append(frameobject)

    def play(self):
        self.preload()

        while True:
            for frameobject in self.frames:
                starttime = time.monotonic()
                self.display.image(frameobject.image)
                while time.monotonic() < (starttime + frameobject.duration / 1000):
                    pass

    def postFrame(self):
        frame = self.frames[self.index]
        self.display.image(frame.image)
        self.index += 1
        if self.index >= self.framecount:
            self.index = 0

        return frame.duration

if __name__ == '__main__':
    display = displayEmulator.DisplayEmulator()
    display.begin()
    logo = AnimatedGif(display)
    logo.preload("out.gif")

    while True:
        #print('loop')
        logo.postFrame()
        time.sleep(0.1)