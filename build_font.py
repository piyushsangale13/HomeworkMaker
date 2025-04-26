import os
from PIL import Image
import cv2
import numpy as np
from ufoLib2 import Font
from fontmake.font_project import FontProject

# ============ SETTINGS ============
IMAGE_FOLDER   = "images"
FONT_NAME      = "MyHandwriting"
OUTPUT_STYLE   = "Regular"
USE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
VARIANTS       = 3
# ==================================

def image_to_outline(img_path):
    """
    Load grayscale image, inset by a border to remove the box outline,
    then threshold+blur and return handwriting contours.
    """
    img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
    h, w = img.shape

    # inset by 5% of min dimension (to drop the rectangle border)
    border = int(min(h, w) * 0.05)
    inner = img[border:h-border, border:w-border]

    # blur + Otsu threshold for clean binary
    blur = cv2.GaussianBlur(inner, (5, 5), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255,
        cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU
    )

    # find contours of handwriting
    contours, _ = cv2.findContours(
        thresh,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    return contours, (h, w), border

def contour_to_glyph(glyph, contours, img_shape, border, scale_factor=1.5):
    """
    Given contours in the inset image, shift them back into
    the full image coordinate space and scale them to enlarge,
    then draw into the glyph.
    """
    pen = glyph.getPen()
    h = img_shape[0]

    # Calculate the bounding box of the contour to set glyph width
    min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

    for contour in contours:
        if cv2.contourArea(contour) < 20:
            continue  # skip tiny noise

        pts = contour.reshape(-1, 2)
        first = True
        for x_in, y_in in pts:
            # shift back into full image
            x = float(x_in + border)
            y = float(y_in + border)
            # flip Y (font coords)
            y = h - y

            # Scale the coordinates by the scaling factor
            x *= scale_factor
            y *= scale_factor

            if first:
                pen.moveTo((x, y))
                first = False
            else:
                pen.lineTo((x, y))

            # Update the bounding box with the scaled coordinates
            min_x = min(min_x, x)
            max_x = max(max_x, x)
            min_y = min(min_y, y)
            max_y = max(max_y, y)

        pen.closePath()

    # Set the width of the glyph based on the scaled bounding box
    glyph_width = max_x - min_x

    # Optionally add some extra spacing to avoid overlap
    glyph_width += 100  # You can adjust this value to control the spacing

    # Set the advance width for the glyph (spacing between letters)
    glyph.width = glyph_width

def build_font():
    ufo = Font()
    ufo.info.familyName   = FONT_NAME
    ufo.info.styleName    = OUTPUT_STYLE
    ufo.info.unitsPerEm   = 1000
    ufo.info.ascender     = 800
    ufo.info.descender    = -200

    feature_lines = []

    for ch in USE_CHARACTERS:
        alt_names = []

        for i in range(1, VARIANTS + 1):
            fn   = f"{ch}{i}.png"
            path = os.path.join(IMAGE_FOLDER, fn)
            if not os.path.exists(path):
                print(f"❌ Missing {fn}")
                continue

            # default glyph is 'a', alternates are 'a.alt1', 'a.alt2'
            glyph_name = ch if i == 1 else f"{ch}.alt{i-1}"
            glyph = ufo.newGlyph(glyph_name)
            if i == 1:
                glyph.unicodes = [ord(ch)]

            contours, shape, border = image_to_outline(path)
            contour_to_glyph(glyph, contours, shape, border, scale_factor=4.0)  # Set the scale factor here
            print(f"✅ Added {glyph_name}")

            if i > 1:
                alt_names.append(glyph_name)

        # add one substitution line per alternate
        for alt in alt_names:
            feature_lines.append(f"sub {ch}' by {alt};")

    # write the OpenType calt feature
    ufo.features.text = (
        "feature calt {\n    " +
        "\n    ".join(feature_lines) +
        "\n} calt;\n"
    )

    # save UFO and compile to TTF
    ufo_path = f"{FONT_NAME}.ufo"
    ufo.save(ufo_path)

    project = FontProject()
    project.build_ttfs([ufo])
    print(f"\n🎉 Done — {FONT_NAME}-Regular.ttf generated")

if __name__ == "__main__":
    build_font()
