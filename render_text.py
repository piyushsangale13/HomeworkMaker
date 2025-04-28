import freetype
import uharfbuzz as hb
from PIL import Image, ImageDraw

def shape_text(text, font_path, features=None):
    # Load the font face
    face = freetype.Face(font_path)
    face.set_char_size(48 * 64)  # 48 pt

    with open(font_path, "rb") as fontfile:
        fontdata = fontfile.read()

    # Create HarfBuzz font from face
    hb_font = hb.Font(hb.Face(fontdata))
    hb_font.scale = (face.size.height, face.size.height)

    # Create and fill HarfBuzz buffer
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()

    # Use OpenType features like 'calt' (ensure it's passed correctly)
    if features is None:
        features = {"calt": True}

    # Shape the text with the specified features
    hb.shape(hb_font, buf, features)

    # Log the glyph information to verify shaping (optional)
    print("Shaped glyph information:", buf.glyph_infos)

    glyph_info = buf.glyph_infos
    glyph_positions = buf.glyph_positions

    return face, glyph_info, glyph_positions


def render_shaped_text(text, font_path, image_path, img_size=(800, 200)):
    face, glyph_info, glyph_positions = shape_text(text, font_path)

    # Create image
    img = Image.new("RGB", img_size, (0,0,0))
    draw = ImageDraw.Draw(img)

    # Start position for text rendering
    x, y = 50, 100

    for info, pos in zip(glyph_info, glyph_positions):
        gid = info.codepoint
        face.load_glyph(gid, freetype.FT_LOAD_RENDER)
        bitmap = face.glyph.bitmap

        top = face.glyph.bitmap_top
        left = face.glyph.bitmap_left
        w, h = bitmap.width, bitmap.rows

        if w > 0 and h > 0:
            glyph_img = Image.frombytes("L", (w, h), bytes(bitmap.buffer))
            rgb_glyph = Image.merge("RGB", (glyph_img,)*3)
            img.paste(rgb_glyph, (int(x + left), int(y - top)), glyph_img)

        # Advance position
        x += pos.x_advance / 64
        y += pos.y_advance / 64

    # Save the result
    img.save(image_path)
    print(f"✅ Saved image with contextual alternates: {image_path}")


# === USAGE EXAMPLE ===
text = "aabbbccdeeefghi sasasa"  # Modify this text to test `calt` behavior
font_path = "master_ttf/MyHandwriting.ttf"  # Replace with your actual font path
output_image = "shaped_text_output.png"

render_shaped_text(text, font_path, output_image)
