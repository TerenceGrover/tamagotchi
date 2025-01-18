from PIL import Image

def calculate_average_color(input_data):
    """
    Calculate the average RGB color of an image or sprite matrix.

    Args:
        input_data (str or list): Path to an image file or a matrix of RGB values.

    Returns:
        tuple: Average RGB color.
    """
    try:
        if isinstance(input_data, str):  # Handle file path
            with Image.open(input_data).convert("RGB") as img:
                pixels = list(img.getdata())
        elif isinstance(input_data, list):  # Handle sprite matrix
            pixels = [pixel for row in input_data for pixel in row]
        else:
            raise ValueError("Invalid input type. Must be file path or matrix.")

        total_color = [0, 0, 0]
        for pixel in pixels:
            total_color[0] += pixel[0]
            total_color[1] += pixel[1]
            total_color[2] += pixel[2]

        num_pixels = len(pixels)
        return tuple(color // num_pixels for color in total_color)
    except Exception as e:
        raise ValueError(f"Error processing input: {e}")
