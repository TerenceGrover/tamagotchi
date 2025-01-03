import time
import pygame

class Controls:
    def __init__(self):
        self.left_button = False
        self.last_press_time = 0  # Timestamp of the last button press
        self.debounce_interval = 0.3  # Debounce interval in seconds

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Check if the left button ('q') is pressed
        if keys[pygame.K_q]:
            current_time = time.time()
            if current_time - self.last_press_time > self.debounce_interval:
                self.left_button = True
                self.last_press_time = current_time
            else:
                self.left_button = False
        else:
            self.left_button = False
