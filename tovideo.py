import subprocess
import glob
import os

filenames = glob.glob('*.png')
path = os.path.abspath("").replace("\\", "/")
print(path)
duration = 0.05

with open("ffmpeg_input.txt", "wb") as outfile:
    for filename in filenames:
        outfile.write(f"file '{path}/{filename}'\n".encode())
        outfile.write(f"duration {duration}\n".encode())

command_line = f"ffmpeg -r 15 -f concat -safe 0 -i ffmpeg_input.txt {path}\\out.gif"
print(command_line)

pipe = subprocess.Popen(command_line, shell=True, stdout=subprocess.PIPE).stdout
output = pipe.read().decode()
pipe.close()
