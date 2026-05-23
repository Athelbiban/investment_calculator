import time
import sys
import threading


class Animation:

    def __init__(self):
        self.stop_animation = False
        self.pause_animation = False

    def animation_func(self):
        animation = [".  ", ".. ", "...", " ..", "  .", "   "]
        idx = 0
        while not self.stop_animation:
            sys.stdout.write(
                f"\rПожалуйста, подождите{animation[idx % len(animation)]}"
            )
            sys.stdout.flush()
            idx += 1
            time.sleep(0.4)
        sys.stdout.write("\r" + " " * 80 + "\r")
        sys.stdout.flush()

    def start_animation_func(self):
        self.stop_animation = False
        t = threading.Thread(target=self.animation_func)
        t.daemon = True
        t.start()

    def stop_animation_func(self):
        self.stop_animation = True
        time.sleep(0.5)
