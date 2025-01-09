from PIL import Image, ImageDraw, ImageFont

def text_to_matrix(text, font_path, font_size, width, height):
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
