import pygame
import random
import time
from core.graphics import Graphics
from core.controls import Controls
from core.states import States

# Constants
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
PIXEL_SIZE = 20
FPS = 30

def main():
    # Initialize Pygame
    pygame.init()
    screen_width = MATRIX_WIDTH * PIXEL_SIZE
    screen_height = MATRIX_HEIGHT * PIXEL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Tamagotchi Movement")

    # Initialize modules
    controls = Controls()
    states = States()
    graphics = Graphics(screen, MATRIX_WIDTH, MATRIX_HEIGHT, PIXEL_SIZE)
    sprite_folder = states.get_sprite_folder()
    sprites = graphics.load_sprites(sprite_folder)
    sprites = tuple(sprites)  # Convert to immutable tuple


    # Game variables
    current_sprite_index = 0
    last_switch_time = time.time()
    switch_interval = random.uniform(0.5, 2.0)

    # Game loop
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Handle inputs
        controls.handle_input()

        # Clear the screen
        graphics.clear_screen()

        # Move sprite
        sprite_matrix = sprites[current_sprite_index]
        sprite_width = len(sprite_matrix[0])
        sprite_height = len(sprite_matrix)
        graphics.move_sprite(sprite_width, sprite_height)
        graphics.clear_screen()
        graphics.draw_sprite(sprite_matrix)

        # Check if it's time to switch the sprite
        current_time = time.time()
        if current_time - last_switch_time > switch_interval:
            current_sprite_index = (current_sprite_index + 1) % len(sprites)
            last_switch_time = current_time
            switch_interval = random.uniform(0.5, 2.0)

        # Ensure the current sprite is valid
        if current_sprite_index < len(sprites):
            sprite_matrix = sprites[current_sprite_index]
        else:
            print(f"Invalid sprite index: {current_sprite_index}")
            sprite_matrix = [[(0, 0, 0) for _ in range(10)] for _ in range(10)]  # Fallback to blank sprite


        # Draw the current sprite
        graphics.draw_sprite(sprite_matrix)


        # Update the display
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
