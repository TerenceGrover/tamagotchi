class Stats:
    def __init__(self):
        self.stats = {
            "food": 80,
            "rest": 60,
            "safe": 70,
            "social": 50,
            "esteem": 90,
        }

    def get_stats(self):
        return self.stats

    def update_stat(self, stat_name, value):
        if stat_name in self.stats:
            self.stats[stat_name] = max(0, min(100, value))  # Clamp values

    def render_stats_screen(self, graphics):
        """
        Render the stats screen on the LED matrix.

        Args:
            graphics (Graphics): Graphics module for rendering.
        """
        rows = [
            f"F:{self.stats['food']}%",
            f"R:{self.stats['rest']}%",
            f"S:{self.stats['safe']}%",
            f"So:{self.stats['social']}%",
            f"E:{self.stats['esteem']}%",
        ]

        for i, row in enumerate(rows):
            for j, char in enumerate(row):
                # Render each character
                pixel_color = (255, 255, 255)  # White text
                graphics.screen.fill(pixel_color, (
                    j * graphics.pixel_size,
                    i * graphics.pixel_size,
                    graphics.pixel_size - 1,
                    graphics.pixel_size - 1
                ))
