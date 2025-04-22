from gpiozero import Button

class Controls:
    def __init__(self):
        self.left = Button(5, pull_up=True)
        self.right = Button(6, pull_up=True)
        self.center = Button(26, pull_up=True)

    def handle_input(self):
        self.left_button = self.left.is_pressed
        self.right_button = self.right.is_pressed
        self.center_button = self.center.is_pressed
