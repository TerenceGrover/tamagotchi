import time
from utils.text_utils import text_to_matrix

class Stats:
    def __init__(self):
        self.stats = {
            "food": 50,
            "rest": 50,
            "safe": 50,
            "social": 50,
            "esteem": 50,
            "education": 0,
            "money": 50
        }
        self.last_update_time = time.time()
        self.decay_rates = {
            "food": 1,
            "rest": 1,
            "social": 1
        }
        self.decay_interval = 10
        self.font_path = "assets/fonts/tamzen.ttf"
        self.font_size = 11

    def decay_stats(self):
        current_time = time.time()
        if current_time - self.last_update_time >= self.decay_interval:
            for stat in self.decay_rates:
                self.stats[stat] = max(0, self.stats[stat] - self.decay_rates[stat])
            self.last_update_time = current_time

    def modify_stat(self, stat, amount):
        if stat in self.stats:
            self.stats[stat] = max(0, min(120, self.stats[stat] + amount))  # Keep within 0-100
            print(f"Updated {stat}: {self.stats[stat]}")

    def update_education_stats(self, education_level, student_loan = 0):
        """
        Update the education and money stats based on the chosen education level and loan.

        Args:
            education_level (str): The chosen education level.
            student_loan (int): The cost associated with the education.
        """
        self.stats["education"] = education_level
        self.stats["money"] = max(0, self.stats["money"] - student_loan / 1000)  # Deduct loan, ensuring non-negative money

        print(self.stats['money'])

    def render_stats_screen(self, graphics):
        stats_left_keys = ["food", "rest", "safe"]
        stats_right_keys = ["social", "esteem"]

        total_rows = max(len(stats_left_keys), len(stats_right_keys))
        row_height = graphics.matrix_height // total_rows

        def get_color(value):
            if value > 80:
                return (150, 255, 150)  # Green
            elif value < 20:
                return (255, 150, 150)  # Red
            else:
                return (255, 255, 255)  # White

        # Draw left stats
        for row_index, stat_key in enumerate(stats_left_keys):
            stat_value = max(0, min(100, self.stats[stat_key]))
            row_text = f"{stat_key[0].upper() if stat_key != 'safe' else 'Sa'}:{stat_value}"
            text_matrix = text_to_matrix(
                row_text,
                self.font_path,
                self.font_size,
                graphics.matrix_width // 2,
                row_height,
            )
            color = get_color(stat_value)
            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):
                        screen_x = x * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.draw.rectangle(
                            [screen_x, screen_y, screen_x + graphics.pixel_size - 1, screen_y + graphics.pixel_size - 1],
                            fill=color
                        )

        # Draw right stats
        for row_index, stat_key in enumerate(stats_right_keys):
            stat_value = self.stats[stat_key]
            row_text = f"{stat_key[:2].capitalize()}:{stat_value}"
            text_matrix = text_to_matrix(
                row_text,
                self.font_path,
                self.font_size,
                graphics.matrix_width // 2,
                row_height,
            )
            color = get_color(stat_value)
            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):
                        screen_x = (graphics.matrix_width // 2 + x) * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.draw.rectangle(
                            [screen_x, screen_y, screen_x + graphics.pixel_size - 1, screen_y + graphics.pixel_size - 1],
                            fill=color
                        )
    def check_win_condition(stats):
        # You win if all stats except education are >= 90
        tracked_stats = ["food", "rest", "safe", "social", "esteem", "money"]
        return all(stats.stats[s] >= 90 for s in tracked_stats)


    def check_lose_condition(self):
        for key in ["food", "rest", "safe", "social", "esteem"]:
            if self.stats[key] <= 0:
                return key  # return the cause of death
        return None
