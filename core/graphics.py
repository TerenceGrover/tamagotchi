import time
import random
from PIL import Image
import pygame
import os

class Graphics:
    def __init__(self, screen, matrix_width, matrix_height, pixel_size):
        self.screen = screen
        self.matrix_width = matrix_width
        self.matrix_height = matrix_height
        self.pixel_size = pixel_size
        self.position = [matrix_width // 2, matrix_height // 2]
        self.last_move_time = time.time()
        self.last_switch_time = time.time()
        self.switch_interval = random.uniform(0.5, 2.0)
        self.pause_duration = random.uniform(1, 3)
        self.sprites = []
        self.current_sprite_index = 0
        self.black = (0,0,0)
        self.frame_x = int(matrix_width // 10)
        self.frame_y = int(matrix_height // 10)
        self.frame_width = int(matrix_width // 1.2)
        self.frame_height = int(matrix_height // 1.2)

    def load_sprites(self, folder_path):
        sprites = []
        for filename in sorted(os.listdir(folder_path)):
            if filename.endswith(".png"):
                filepath = os.path.join(folder_path, filename)
                img = Image.open(filepath).convert("RGB")
                img = img.resize((10, 10))
                matrix = [[img.getpixel((x, y)) for x in range(10)] for y in range(10)]
                sprites.append(matrix)
        if not sprites:
            raise ValueError(f"No sprites found in {folder_path}")
        return sprites

    def set_sprites(self, new_sprites):
        """
        Update sprites and reset the sprite index.
        """
        self.sprites = new_sprites
        self.current_sprite_index = 0

    def switch_sprite(self):
        current_time = time.time()
        if current_time - self.last_switch_time > self.switch_interval:
            self.current_sprite_index = (self.current_sprite_index + 1) % len(self.sprites)
            self.last_switch_time = current_time
            self.switch_interval = random.uniform(0.5, 2.0)

    def update_sprites(self, states):
        """
        Update sprites based on the current state of life.
        """
        sprite_folder = states.get_sprite_folder()
        self.set_sprites(self.load_sprites(sprite_folder))

    def move_sprite(self):
        current_time = time.time()
        if current_time - self.last_move_time > self.pause_duration:
            direction = random.choice(["left", "right", "up", "down"])
            if direction == "left" and self.position[0] > self.frame_x:
                self.position[0] -= 1
            elif direction == "right" and self.position[0] < self.frame_x + self.frame_width - 10:
                self.position[0] += 1
            elif direction == "up" and self.position[1] > self.frame_y:
                self.position[1] -= 1
            elif direction == "down" and self.position[1] < self.frame_y + self.frame_height - 10:
                self.position[1] += 1
            self.last_move_time = current_time
            self.pause_duration = random.uniform(1, 3)
            
    def draw_frame(self):
        """
        Draw the frame as matrix pixels with outlines and add points for game categories.
        """
        # Draw the frame with outlined pixels
        for x in range(self.frame_x, self.frame_x + self.frame_width):
            # Top line
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),  # Black outline
                (x * self.pixel_size - 1, self.frame_y * self.pixel_size - 1, self.pixel_size + 2, self.pixel_size + 2),
            )
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),  # White pixel
                (x * self.pixel_size, self.frame_y * self.pixel_size, self.pixel_size - 2, self.pixel_size - 2),
            )
            # Bottom line
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),  # Black outline
                (x * self.pixel_size - 1, (self.frame_y + self.frame_height - 1) * self.pixel_size - 1, self.pixel_size + 2, self.pixel_size + 2),
            )
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),  # White pixel
                (x * self.pixel_size, (self.frame_y + self.frame_height - 1) * self.pixel_size, self.pixel_size - 2, self.pixel_size - 2),
            )
        for y in range(self.frame_y, self.frame_y + self.frame_height):
            # Left line
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),  # Black outline
                (self.frame_x * self.pixel_size - 1, y * self.pixel_size - 1, self.pixel_size + 2, self.pixel_size + 2),
            )
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),  # White pixel
                (self.frame_x * self.pixel_size, y * self.pixel_size, self.pixel_size - 2, self.pixel_size - 2),
            )
            # Right line
            pygame.draw.rect(
                self.screen,
                (0, 0, 0),  # Black outline
                ((self.frame_x + self.frame_width - 1) * self.pixel_size - 1, y * self.pixel_size - 1, self.pixel_size + 2, self.pixel_size + 2),
            )
            pygame.draw.rect(
                self.screen,
                (255, 255, 255),  # White pixel
                ((self.frame_x + self.frame_width - 1) * self.pixel_size, y * self.pixel_size, self.pixel_size - 2, self.pixel_size - 2),
            )

    def draw_frame_and_points(self, selected_point_index):
        """
        Draw the frame and points, with the selected point flashing.
        """
        # Frame drawing code remains the same
        self.draw_frame()

        # Define the points
        top_points = [
            (self.frame_x + self.frame_width // 7, self.frame_y - 2),
            (self.frame_x + self.frame_width // 2, self.frame_y - 2),
            (self.frame_x + 6 * self.frame_width // 7, self.frame_y - 2),
        ]
        bottom_points = [
            (self.frame_x + self.frame_width // 7, self.frame_y + self.frame_height + 1),
            (self.frame_x + self.frame_width // 2, self.frame_y + self.frame_height + 1),
            (self.frame_x + 6 * self.frame_width // 7, self.frame_y + self.frame_height + 1),
        ]
        all_points = top_points + bottom_points

        # Draw the points
        current_time = time.time()
        for i, (x, y) in enumerate(all_points):
            # Determine if the point should flash
            if i == selected_point_index and int(current_time * 2) % 2 == 0:
                color = (0, 0, 0)  # Flashing makes the point "invisible"
            else:
                color = (255, 0, 0)  # Red point

            # Draw the point
            pygame.draw.rect(
                self.screen,
                color,
                (x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size),
            )


    def draw_sprite(self):
        sprite_matrix = self.sprites[self.current_sprite_index]
        for y, row in enumerate(sprite_matrix):
            for x, pixel in enumerate(row):
                screen_x = (self.position[0] + x) * self.pixel_size
                screen_y = (self.position[1] + y) * self.pixel_size
                pygame.draw.rect(
                    self.screen,
                    pixel,
                    (screen_x, screen_y, self.pixel_size - 1, self.pixel_size - 1),
                )

    def draw_home_screen(self, selected_point_index):
        """
        Draw the home screen, including the frame and flashing points.
        """
        self.clear_screen()
        self.draw_frame_and_points(selected_point_index)
        self.switch_sprite()
        self.move_sprite()
        self.draw_sprite()

    def draw_game_screen(self, game_index):
        """
        Draw a game screen based on the selected point.
        """
        self.clear_screen()
        # Render a placeholder for the game screen
        pygame.draw.rect(
            self.screen,
            (random.randint(0, 255), 255, random.randint(0, 255)),  # Green rectangle for demo purposes
            (self.matrix_width * 7.5, self.pixel_size * 7.5, self.pixel_size * 7.5, self.pixel_size * 7.5),
        )
        pygame.display.set_caption(f"Game {game_index + 1}")  # Update window title

    def clear_screen(self):
        """Clear the screen by filling it with black."""
        self.screen.fill(self.black)
