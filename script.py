import pygame
from PIL import Image
import os
import random
import time

# Constants
MATRIX_WIDTH = 64  # LED matrix width
MATRIX_HEIGHT = 32  # LED matrix height
PIXEL_SIZE = 20  # Size of each "LED pixel" on the screen
FPS = 30  # Frames per second
BLACK = (0, 0, 0)

# Function to load all sprites from a folder
def load_sprites(folder_path, matrix_width, matrix_height):
    """
    Load all sprites from a folder and convert them into RGB matrices.

    Args:
        folder_path (str): Path to the folder containing sprite images.
        matrix_width (int): Width of the LED matrix.
        matrix_height (int): Height of the LED matrix.

    Returns:
        list: List of RGB matrices representing the sprites.
    """
    sprites = []
    for filename in sorted(os.listdir(folder_path)):
        if filename.endswith(".png"):
            filepath = os.path.join(folder_path, filename)
            img = Image.open(filepath).convert("RGB")
            img = img.resize((matrix_width, matrix_height))
            matrix = []
            for y in range(matrix_height):
                row = []
                for x in range(matrix_width):
                    row.append(img.getpixel((x, y)))  # (R, G, B) tuple
                matrix.append(row)
            sprites.append(matrix)
    return sprites

# Function to draw a sprite matrix onto the screen
def draw_sprite(screen, sprite_matrix):
    for y, row in enumerate(sprite_matrix):
        for x, pixel in enumerate(row):
            pygame.draw.rect(
                screen,
                pixel,  # (R, G, B) color
                (x * PIXEL_SIZE, y * PIXEL_SIZE, PIXEL_SIZE - 1, PIXEL_SIZE - 1),
            )

# Initialize Pygame
pygame.init()
screen_width = MATRIX_WIDTH * PIXEL_SIZE
screen_height = MATRIX_HEIGHT * PIXEL_SIZE
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tamagotchi Movement")

# Load sprites for a specific state
sprite_folder = "sprites/whore1/adult"  # Adjust the path as needed
sprites = load_sprites(sprite_folder, MATRIX_WIDTH, MATRIX_HEIGHT)

# Game variables
current_sprite_index = 0
last_switch_time = time.time()
switch_interval = random.uniform(0.5, 2.0)  # Random time between sprite changes

# Game loop
clock = pygame.time.Clock()
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Clear the screen
    screen.fill(BLACK)

    # Check if it's time to switch the sprite
    current_time = time.time()
    if current_time - last_switch_time > switch_interval:
        current_sprite_index = (current_sprite_index + 1) % len(sprites)
        last_switch_time = current_time
        switch_interval = random.uniform(0.5, 2.0)  # Generate a new random interval

    # Draw the current sprite
    draw_sprite(screen, sprites[current_sprite_index])

    # Update the display
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
