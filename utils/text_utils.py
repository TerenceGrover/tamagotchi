from PIL import Image, ImageDraw, ImageFont

def text_to_matrix(text, font_path, font_size, width, height, color = "white"):
    """
    Convert text into an RGB matrix.

    Args:
        text (str): The text to render.
        font_path (str): Path to the font file.
        font_size (int): Font size to use for rendering.
        width (int): The width of the output matrix.
        height (int): The height of the output matrix.

    Returns:
        list: An RGB matrix representing the text.
    """
    font = ImageFont.truetype(font_path, font_size)
    img = Image.new("RGB", (width, height), "black")
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill="white")

    # Convert image to matrix
    matrix = [
        [img.getpixel((x, y)) for x in range(width)]
        for y in range(height)
    ]
    return matrix

def split_text_to_lines(text, max_chars_per_line=8):
    """
    Splits a string into multiple lines if it exceeds the max characters per line.
    Adds a line break between segments closest to a space or just hard-wraps if needed.
    """
    if len(text) <= max_chars_per_line:
        return [text]

    words = text.split(" ")
    lines = []
    current_line = ""

    for word in words:
        if len(current_line) + len(word) + 1 <= max_chars_per_line:
            if current_line:
                current_line += " "
            current_line += word
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    return lines

def draw_money_signal(draw, x, y, value, pixel_size):
    """
    Draws signal bars next to the dollar sign based on the money value.
    - `draw`: your graphics.draw
    - `x`, `y`: top-left corner where the first bar starts (right of the $ symbol)
    - `value`: current money value
    - `pixel_size`: size of one pixel (scale)
    """
    thresholds = [10, 25, 50, 75]  # 4 bars total
    colors = [
        (255, 50, 50),     # Red
        (255, 165, 0),     # Orange
        (255, 255, 0),     # Yellow
        (0, 255, 0),       # Green
    ]
    
    bar_spacing = 2 * pixel_size
    bar_width = pixel_size * 3
    max_bar_height = 4 * pixel_size

    bars = sum(value >= t for t in thresholds)

    for i in range(bars):
        bar_height = (i * 2 + 1) * pixel_size
        top_left_x = x + i * (bar_width + bar_spacing)
        top_left_y = y + (max_bar_height - bar_height)

        draw.rectangle(
            [
                top_left_x,
                top_left_y,
                top_left_x + bar_width - 1,
                top_left_y + bar_height - 1,
            ],
            fill=colors[i]
        )
