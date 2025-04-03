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
