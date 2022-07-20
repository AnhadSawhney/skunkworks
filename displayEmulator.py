import tkinter as tk
from PIL import Image, ImageTk
import threading, time
import animatedGIF

#display.image(frame_object.image)

class DisplayEmulator:
    def __init__(self):
        self.width = 240
        self.height = 135
        self.keep_looping = True
        self.new_image_ready = False
        self.current_image = None
    
    def begin(self):
        self.t = threading.Thread(target=self.loop)
        self.t.start()

    def loop(self):
        print("Display Emulator Loop Start!")
        root = tk.Tk() #tk.Toplevel()
        root.title('Raspberry Pi TFT')
        root.geometry('{}x{}'.format(self.width, self.height))
        label = tk.Label(root)
        label.pack()
        root.protocol("WM_DELETE_WINDOW", self.on_closing)

        while self.keep_looping:
            if self.new_image_ready:
                self.new_image_ready = False
                try:
                    im = ImageTk.PhotoImage(self.current_image) # THIS MUST BE SAVED AS ITS OWN VARIABLE OTHERWISE IT GETS GARBAGE COLLECTED BEFORE IT GETS TO THE SCREEN
                except:
                    continue
                label.config(image=im)
                label.pack()
                root.update()

            #self.root.update()
            time.sleep(0.05)

        root.destroy()

    def image(self, frame):
        self.current_image = frame
        self.new_image_ready = True

    def on_closing(self): 
        self.keep_looping = False 
        #self.t.join()

