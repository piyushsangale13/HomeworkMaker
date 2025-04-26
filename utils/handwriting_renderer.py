from PIL import Image, ImageDraw
import cv2
import numpy as np
import string

def segment_characters(image_path):
    """
    Detect characters from a full-page handwriting sample.
    Assumes characters A-Z followed by 0-9 are written clearly (in any layout).
    """
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    _, thresh = cv2.threshold(img, 180, 255, cv2.THRESH_BINARY_INV)

    # Morphological operation to reduce noise
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
    thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

    # Find contours of characters
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bounding_boxes = [cv2.boundingRect(c) for c in contours]
    
    # Sort by rows then columns (top to bottom, then left to right)
    def sort_key(bbox):
        x, y, w, h = bbox
        return (y // 20) * 10000 + x  # rough row separation by y // 20

    sorted_boxes = sorted(bounding_boxes, key=sort_key)

    expected_chars = string.ascii_uppercase + string.digits
    if len(sorted_boxes) < len(expected_chars):
        print("Warning: Fewer characters detected than expected.")

    characters = {}
    for i, box in enumerate(sorted_boxes[:len(expected_chars)]):
        x, y, w, h = box
        char_img = img[y:y+h, x:x+w]
        pil_char = Image.fromarray(255 - char_img)
        characters[expected_chars[i]] = pil_char

    return characters

def render_handwriting(sample_path, text, output_path):
    characters = segment_characters(sample_path)
    canvas = Image.new('L', (1200, 800), color=255)
    draw = ImageDraw.Draw(canvas)

    x, y = 20, 20
    for char in text.upper():
        if char == '\n':
            y += 60
            x = 20
            continue
        elif char == ' ':
            x += 25
            continue
        elif char not in characters:
            continue

        ch_img = characters[char]
        canvas.paste(ch_img, (x, y))
        x += ch_img.width + 10

        if x > 1000:
            y += 60
            x = 20

    canvas.save(output_path)
