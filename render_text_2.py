import uharfbuzz as hb
import freetype
from PIL import Image, ImageDraw
import numpy as np

# Settings
FONT_PATH = "master_ttf\MyHandwriting.ttf"
TEXT = "hello world"
OUTPUT_IMAGE = "output.png"
FONT_SIZE = 128
MARGIN = 20
EXTRA_SPACE = 400  # Add extra spacing after each space character

def shape_text(fontdata, text):
    face = freetype.Face(FONT_PATH)
    face.set_char_size(FONT_SIZE * 64)

    hb_font = hb.Font(hb.Face(fontdata))
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(hb_font, buf, features={"calt": True})

    infos = buf.glyph_infos
    positions = buf.glyph_positions

    glyphs = []
    for info, pos in zip(infos, positions):
        glyph_index = info.codepoint
        x_advance = pos.x_advance / 64
        y_advance = pos.y_advance / 64
        x_offset = pos.x_offset / 64
        y_offset = pos.y_offset / 64
        glyphs.append((glyph_index, x_advance, y_advance, x_offset, y_offset))

    return glyphs

def render_text(text):
    with open(FONT_PATH, "rb") as f:
        fontdata = f.read()

    glyphs = shape_text(fontdata, text)

    # Calculate image size
    img_width = int(sum(g[1] for g in glyphs) + 2 * MARGIN + text.count(' ') * EXTRA_SPACE)
    img_height = FONT_SIZE + 2 * MARGIN
    image = Image.new("RGB", (img_width, img_height), color=(255, 255, 255))  # White background
    draw = ImageDraw.Draw(image)

    face = freetype.Face(FONT_PATH)
    face.set_char_size(FONT_SIZE * 64)

    pen_x = MARGIN
    pen_y = MARGIN
    for i, (glyph_index, x_advance, y_advance, x_offset, y_offset) in enumerate(glyphs):
        face.load_glyph(glyph_index, freetype.FT_LOAD_RENDER)
        bitmap = face.glyph.bitmap
        top = face.glyph.bitmap_top
        left = face.glyph.bitmap_left

        glyph_img = np.array(bitmap.buffer, dtype=np.uint8).reshape(bitmap.rows, bitmap.width)

        y = int(pen_y + FONT_SIZE - top)
        x = int(pen_x + x_offset + left)

        for r in range(bitmap.rows):
            for c in range(bitmap.width):
                val = glyph_img[r, c]
                if val > 0:
                    if 0 <= (x+c) < image.width and 0 <= (y+r) < image.height:
                        image.putpixel((x+c, y+r), (0, 0, 0))  # Black ink

        pen_x += x_advance

        # Add extra spacing after space character
        if chr(glyph_index) == ' ':
            pen_x += EXTRA_SPACE

    return image

if __name__ == "__main__":
    image = render_text(TEXT)
    image.save(OUTPUT_IMAGE)
    print(f"✅ Text rendered and saved to {OUTPUT_IMAGE}")
