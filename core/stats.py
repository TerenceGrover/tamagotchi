import time
from utils.text_utils import text_to_matrix

class Stats:
    def __init__(self):
        self.stats = {
            "food": 80,
            "rest": 60,
            "safe": 70,
            "social": 50,
            "esteem": 90,
        }
        self.last_update_time = time.time()
        self.decay_rates = {
            "food": 1,
            "rest": 1,
            "social": 1,
        }
        self.decay_interval = 5
        self.font_path = "assets/fonts/tamzen.ttf"
        self.font_size = 11

    def decay_stats(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.decay_interval:
            for stat in self.decay_rates:
                self.stats[stat] = max(0, self.stats[stat] - self.decay_rates[stat])
            self.last_update_time = current_time

    def render_stats_screen(self, graphics):
        stats_left = [
            f"F:{self.stats['food']}",
            f"R:{self.stats['rest']}",
            f"Sa:{self.stats['safe']}",
        ]
        stats_right = [
            f"So:{self.stats['social']}",
            f"E:{self.stats['esteem']}",
        ]

        total_rows = max(len(stats_left), len(stats_right))
        row_height = graphics.matrix_height // total_rows

        for row_index, row in enumerate(stats_left):
            text_matrix = text_to_matrix(
                row,
                self.font_path,
                self.font_size,
                graphics.matrix_width // 2,
                row_height,
            )

            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):
                        screen_x = x * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.screen.fill(pixel, (
                            screen_x,
                            screen_y,
                            graphics.pixel_size - 1,
                            graphics.pixel_size - 1,
                        ))

        for row_index, row in enumerate(stats_right):
            text_matrix = text_to_matrix(
                row,
                self.font_path,
                self.font_size,
                graphics.matrix_width // 2,
                row_height,
            )

            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):
                        screen_x = (graphics.matrix_width // 2 + x) * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.screen.fill(pixel, (
                            screen_x,
                            screen_y,
                            graphics.pixel_size - 1,
                            graphics.pixel_size - 1,
                        ))
