from PIL import Image, ImageDraw, ImageFont

class Stats:
    def __init__(self):
        self.stats = {
            "food": 80,
            "rest": 60,
            "safe": 70,
            "social": 50,
            "esteem": 90,
        }
        self.font = ImageFont.truetype("assets/fonts/tamzen.ttf", 11)  # Load a small font

    def text_to_matrix(self, text, width, height):
        """
        Convert text into an RGB matrix.

        Args:
            text (str): The text to render.
            width (int): The width of the output matrix.
            height (int): The height of the output matrix.

        Returns:
            list: An RGB matrix representing the text.
        """
        img = Image.new("RGB", (width, height), "black")
        draw = ImageDraw.Draw(img)
        draw.text((0, 0), text, font=self.font, fill="white")

        # Convert image to matrix
        matrix = [
            [img.getpixel((x, y)) for x in range(width)]
            for y in range(height)
        ]
        return matrix

    def render_stats_screen(self, graphics):
        """
        Render the stats screen on the LED matrix, split into two columns.

        Args:
            graphics (Graphics): Graphics module for rendering.
        """
        stats_left = [
            f"F:{self.stats['food']}",
            f"R:{self.stats['rest']}",
            f"Sa:{self.stats['safe']}",
        ]
        stats_right = [
            f"So:{self.stats['social']}",
            f"E:{self.stats['esteem']}",
        ]

        # Calculate row height for better readability
        total_rows = max(len(stats_left), len(stats_right))
        row_height = graphics.matrix_height // total_rows

        # Render left column
        for row_index, row in enumerate(stats_left):
            text_matrix = self.text_to_matrix(
                row,
                graphics.matrix_width // 2,  # Half width for left column
                row_height
            )

            # Render the text matrix for the left column
            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):  # Skip black pixels
                        screen_x = x * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.screen.fill(pixel, (
                            screen_x,
                            screen_y,
                            graphics.pixel_size - 1,
                            graphics.pixel_size - 1
                        ))

        # Render right column
        for row_index, row in enumerate(stats_right):
            text_matrix = self.text_to_matrix(
                row,
                graphics.matrix_width // 2,  # Half width for right column
                row_height
            )

            # Render the text matrix for the right column
            for y, row_pixels in enumerate(text_matrix):
                for x, pixel in enumerate(row_pixels):
                    if pixel != (0, 0, 0):  # Skip black pixels
                        screen_x = (graphics.matrix_width // 2 + x) * graphics.pixel_size
                        screen_y = (row_index * row_height + y) * graphics.pixel_size
                        graphics.screen.fill(pixel, (
                            screen_x,
                            screen_y,
                            graphics.pixel_size - 1,
                            graphics.pixel_size - 1
                        ))
