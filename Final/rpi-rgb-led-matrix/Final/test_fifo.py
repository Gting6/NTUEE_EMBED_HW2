import io
import os
import time

base_line = 'abcdefghijklmnopqrstuvwxyz'
data = (base_line * 10000 + '\n').encode()

file_name = './panel.fifo'
if not os.path.exists(file_name):
    os.mkfifo(file_name)
fd = os.open(file_name, os.O_WRONLY)
# os.O_NONBLOCK makes os.set_blocking(fd, False) unnecessary.
print("test")
with io.FileIO(fd, 'wb') as f:
    written = 0
    while written < len(data):
        print("test2")
        n = f.write(data[written:])
        if n is None:
            time.sleep(.5)
        else:
            written += n