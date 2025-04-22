import time
from PIL import Image, ImageDraw
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from core.graphics import Graphics
from core.controls import Controls
from core.states import States
from core.stats import Stats
from core.minigames.platformer import update_platforms, check_goal_reached, handle_input, draw_platformer, calculate_jump_curve
from core.minigames.education import handle_education_input, render_education_screen
from core.minigames.social import handle_social_input, initialize_socializing
from core.minigames.housing import initialize_housing, handle_housing_input, assign_real_estate_agent
from core.minigames.hobby import initialize_hobby, update_hobby
from core.minigames.job import initialize_job, update_job, apply_job_rewards

# Matrix configuration
MATRIX_WIDTH = 64
MATRIX_HEIGHT = 32
PIXEL_SIZE = 1  # Keep it simple

class SimpleGraphics:
    def __init__(self, matrix):
        self.matrix = matrix
        self.canvas = Image.new("RGB", (MATRIX_WIDTH * PIXEL_SIZE, MATRIX_HEIGHT * PIXEL_SIZE))
        self.draw = ImageDraw.Draw(self.canvas)

    def clear_screen(self):
        self.draw.rectangle([(0, 0), self.canvas.size], fill=(0, 0, 0))

    def draw_sprite(self, path, pos_x, pos_y):
        img = Image.open(path).convert("RGB")
        img = img.resize((10, 10))  # Resize if needed
        for y in range(10):
            for x in range(10):
                color = img.getpixel((x, y))
                if color != (0, 0, 0):  # Skip black
                    screen_x = (pos_x + x) * PIXEL_SIZE
                    screen_y = (pos_y + y) * PIXEL_SIZE
                    self.draw.rectangle([screen_x, screen_y, screen_x + PIXEL_SIZE - 1, screen_y + PIXEL_SIZE - 1], fill=color)

    def render(self):
        # Resize canvas if pixel_size > 1
        display_img = self.canvas.resize((self.matrix.width, self.matrix.height), Image.NEAREST)
        self.matrix.SetImage(display_img)

def main():
    options = RGBMatrixOptions()
    options.rows = MATRIX_HEIGHT
    options.cols = MATRIX_WIDTH
    options.chain_length = 1
    options.parallel = 1

    matrix = RGBMatrix(options=options)
    gfx = SimpleGraphics(matrix)

    while True:
        gfx.clear_screen()
        gfx.draw_sprite("assets/sprites/whore1/adult/sprite0.png", 10, 10)  # Change path if needed
        gfx.render()
        time.sleep(1 / 30)

if __name__ == "__main__":
    main()
