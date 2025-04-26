from PIL import Image, ImageDraw, ImageFont

def render_text_with_font(text, font_path, image_path, font_size=48, img_width=800, img_height=200):
    """
    Render text using a font with contextual alternates into an image using Pillow.

    Parameters:
    - text: The input text to render.
    - font_path: Path to the TTF font file with calt variants.
    - image_path: Output image path where the text will be saved.
    - font_size: The font size to render the text.
    - img_width, img_height: Dimensions of the output image.
    """
    # Load the font using Pillow
    font = ImageFont.truetype(font_path, font_size)

    # Create a blank image with a white background
    image = Image.new("RGB", (img_width, img_height), (255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    # Starting position for rendering text
    x, y = 50, 50

    # Text color (black)
    text_color = (0, 0, 0)

    # Render the text normally using Pillow
    draw.text((x, y), text, font=font, fill=text_color)

    # Save the final image with the text
    image.save(image_path)
    print(f"Image saved as {image_path}")

# Example usage:
text_input = "aabbbccdeeefghi sasasa"
font_path = "master_ttf\MyHandwriting.ttf"  # Replace with your TTF font path
output_image_path = "output_text_image.png"

render_text_with_font(text_input, font_path, output_image_path)
