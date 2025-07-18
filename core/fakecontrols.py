import time
import random

class FakeControls:
    def __init__(self):
        self.left_button = False
        self.right_button = False
        self.center_button = False
        self.last_action = time.time()

    def handle_input(self):
        now = time.time()
        if now - self.last_action > random.uniform(0.5, 2):  # simulate delay
            direction = random.choice(['left', 'center', 'right'])
            setattr(self, f"{direction}_button", True)
            print(f"FAKE PRESS: {direction.upper()}")
            self.last_action = now
        else:
            self.left_button = False
            self.right_button = False
            self.center_button = False
