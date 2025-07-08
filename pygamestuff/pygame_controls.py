import time
import pygame

class Controls:
    def __init__(self):
        self.left_button = False
        self.right_button = False
        self.center_button = False
        self.last_press = time.time()
        self.debounce_interval = 0.2  # 200ms debounce

    def handle_input(self):
        keys = pygame.key.get_pressed()
        current_time = time.time()

        # Left button (Q)
        if keys[pygame.K_q] and current_time - self.last_press > self.debounce_interval:
            self.left_button = True
            self.last_press = current_time
        else:
            self.left_button = False

        # Right button (D) with debounce
        if keys[pygame.K_d] and current_time - self.last_press > self.debounce_interval:
            self.right_button = True
            self.last_press = current_time
        else:
            self.right_button = False

        # Center button (S) with debounce
        if keys[pygame.K_s] and current_time - self.last_press > self.debounce_interval:
            self.center_button = True
            self.last_press = current_time
        else:
            self.center_button = False
