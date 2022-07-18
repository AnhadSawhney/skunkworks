import tkinter as tk
from PIL import Image, ImageTk
import threading, time

#display.image(frame_object.image)

class DisplayEmulator:
    def __init__(self):
        self.width = 240
        self.height = 135
        self.root = tk.Tk() #tk.Toplevel()
        self.root.title('Raspberry Pi TFT')
        self.root.geometry('{}x{}'.format(self.width, self.height))
        self.label = tk.Label(self.root)
        self.label.pack()
        self.keep_looping = True
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.t = threading.Thread(target=self.loop)
        self.t.start()

    def loop(self):
        print("Display Emulator Loop Start!")
        while self.keep_looping:
            self.root.update()
            time.sleep(0.05)

    def image(self, frame):
        self.label.config(image=ImageTk.PhotoImage(frame))
        self.label.pack()
        self.root.update()

    def on_closing(self): 
        self.root.destroy()
        self.keep_looping = False 
        #self.t.join()