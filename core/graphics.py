import pygame
from PIL import Image
import os
import time
import random

class Graphics:
    def __init__(self, screen, matrix_width, matrix_height, pixel_size):
        self.screen = screen
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.pixel_size = pixel_size
        self.black = (0, 0, 0)
        
        # Position and movement attributes
        self.position = [matrix_width // 2, matrix_height // 2]  # Start in the center
        self.last_move_time = time.time()
        self.pause_duration = random.uniform(1, 3)

    def load_sprites(self, folder_path):
        """
        Load all sprites from a folder and convert them into RGB matrices.

        Args:
            folder_path (str): Path to the folder containing sprite images.

        Returns:
            list: List of RGB matrices representing the sprites.
        """
        sprites = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                filepath = os.path.join(folder_path, filename)
                img = Image.open(filepath).convert("RGB")
                
                # Resize sprite to 10x10
                img = img.resize((10, 10))  # Ensure sprites are 10x10
                
                # Convert to RGB matrix
                matrix = []
                for y in range(10):
                    row = []
                    for x in range(10):
                        row.append(img.getpixel((x, y)))  # (R, G, B) tuple
                    matrix.append(row)
                
                # Debugging: Log matrix dimensions
                if len(matrix) != 10 or len(matrix[0]) != 10:
                    print(f"Error: Sprite {filename} is not 10x10")
                sprites.append(matrix)
        return sprites

    def move_sprite(self, sprite_width, sprite_height):
        """
        Randomly move the sprite around with occasional pauses.
        """
        current_time = time.time()
        if current_time - self.last_move_time > self.pause_duration:
            # Randomly move in one direction
            direction = random.choice(["left", "right", "up", "down"])
            if direction == "left" and self.position[0] > 0:
                self.position[0] -= 1
            elif direction == "right" and self.position[0] < self.matrix_width - sprite_width:
                self.position[0] += 1
            elif direction == "up" and self.position[1] > 0:
                self.position[1] -= 1
            elif direction == "down" and self.position[1] < self.matrix_height - sprite_height:
                self.position[1] += 1

            self.last_move_time = current_time
            self.pause_duration = random.uniform(1, 3)

    def draw_sprite(self, sprite_matrix):
        """
        Draw a sprite matrix at the current position on the screen.

        Args:
            sprite_matrix (list): A 2D list representing the sprite's RGB values.
        """
        sprite_height = len(sprite_matrix)
        sprite_width = len(sprite_matrix[0])

        # Debugging: Log sprite dimensions
        print(f"Drawing sprite at position {self.position} with size {sprite_width}x{sprite_height}")

        for y, row in enumerate(sprite_matrix):
            for x, pixel in enumerate(row):
                screen_x = (self.position[0] + x) * self.pixel_size
                screen_y = (self.position[1] + y) * self.pixel_size
                pygame.draw.rect(
                    self.screen,
                    pixel,
                    (screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1),
                )

    def clear_screen(self):
        """Clear the screen by filling it with black."""
        self.screen.fill(self.black)
