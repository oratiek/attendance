import os
import sys
import time

path="/media/keitaro/attendance"
while True:
    print(os.path.exists(path))
    time.sleep(1)
