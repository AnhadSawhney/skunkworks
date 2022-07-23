from PIL import Image, ImageOps
import os
import time

class Frame:
    def __init__(self, duration=0):
        self.duration = duration
        self.image = None

class AnimatedGif:
    def __init__(self, display, rotation, width=None, height=None, folder=None):
        self.framecount = 0
        #self.loop = 0
        self.index = 0
        self.duration = 0
        self.frames = []
        self.rotation = rotation

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
        print("Loading {}".format(file))
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
            print("Loading frame {}".format(i))
            image.seek(i)
            # Create blank image for drawing.
            # Make sure to create image with mode 'RGB' for full color.
            frameobject = Frame(duration=self.duration)
            if "duration" in image.info:
                frameobject.duration = image.info["duration"]

            f = image.convert("RGB")
#            if self.rotation % 180 == 90:
#                f = f.transpose(Image.ROTATE_90)

            frameobject.image = ImageOps.pad(  # pylint: disable=no-member
                f,
                ((self.width, self.height) if self.rotation % 180 == 0 else (self.height, self.width)),
                method=Image.Resampling.NEAREST,
                color=(0, 0, 0),
                centering=(0.5, 0.5),
            )

            self.frames.append(frameobject)

    def play(self):
        self.preload()

        while True:
            for frameobject in self.frames:
                starttime = time.monotonic()
                self.display.image(frameobject.image, self.rotation)
                while time.monotonic() < (starttime + frameobject.duration / 1000):
                    pass

    def postFrame(self):
        frame = self.frames[self.index]
        self.display.image(frame.image, self.rotation)
        self.index += 1
        if self.index >= self.framecount:
            self.index = 0

        return frame.duration

if __name__ == '__main__':
    import displayEmulator
    display = displayEmulator.DisplayEmulator()
    display.begin()
    logo = AnimatedGif(display)
    logo.preload("out.gif")

    while True:
        #print('loop')
        logo.postFrame()
        time.sleep(0.1)