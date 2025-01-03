import pygame

class Controls:
    def __init__(self):
        self.inputs = {
            "left": False,
            "center": False,
            "right": False
        }

    def handle_input(self):
        """
        Update the state of controls based on key presses.
        """
        keys = pygame.key.get_pressed()
        self.inputs["left"] = keys[pygame.K_q]  # "q" for left
        self.inputs["center"] = keys[pygame.K_s]  # "s" for down
        self.inputs["right"] = keys[pygame.K_d]  # "d" for right

    def get_inputs(self):
        """
        Get the current state of the inputs.

        Returns:
            dict: Current state of controls.
        """
        return self.inputs
