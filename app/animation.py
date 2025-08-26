import time
import sys
import threading

stop_animation = False

def animation_func():
    global stop_animation
    animation = [".  ", ".. ", "...", " ..", "  .", "   "]
    idx = 0
    while not stop_animation:
        sys.stdout.write(f"\rПожалуйста, подождите{animation[idx % len(animation)]}")
        sys.stdout.flush()
        idx += 1
        time.sleep(0.4)
    sys.stdout.write("\r" + " " * 80 + "\r")
    sys.stdout.flush()

def start_animation():
    global stop_animation
    stop_animation = False
    t = threading.Thread(target=animation_func)
    t.daemon = True
    t.start()

def stop_animation_func():
    global stop_animation
    stop_animation = True
    time.sleep(0.5)
