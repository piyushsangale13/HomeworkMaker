import os
import shutil  # This module allows us to delete directories

from svgpathtools import svg2paths
from svgpathtools import Line, QuadraticBezier, CubicBezier
from ufoLib2 import Font
from fontmake.font_project import FontProject

# Settings
IMAGE_FOLDER   = "svgs"  # Folder containing SVGs
FONT_NAME      = "MyHandwriting"
OUTPUT_STYLE   = "Regular"
USE_CHARACTERS = "abcdefghijklmnopqrstuvwxyz"
VARIANTS       = 3

TARGET_HEIGHT  = 600  # 👈 Desired height (ascender area). Adjust as needed

def interpolate(p1, p2, t):
    x1, y1 = p1
    x2, y2 = p2
    return (x1 * (1 - t) + x2 * t, y1 * (1 - t) + y2 * t)

def subdivide_cubic(p0, p1, p2, p3, steps=8):
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        p01 = interpolate(p0, p1, t)
        p12 = interpolate(p1, p2, t)
        p23 = interpolate(p2, p3, t)
        p012 = interpolate(p01, p12, t)
        p123 = interpolate(p12, p23, t)
        p0123 = interpolate(p012, p123, t)
        curve_points.append(p0123)
    return curve_points

def subdivide_quadratic(p0, p1, p2, steps=8):
    curve_points = []
    for i in range(steps + 1):
        t = i / steps
        p01 = interpolate(p0, p1, t)
        p12 = interpolate(p1, p2, t)
        p012 = interpolate(p01, p12, t)
        curve_points.append(p012)
    return curve_points

def svg_to_glyph(glyph, svg_path):
    paths, _ = svg2paths(svg_path)

    if not paths:
        print(f"⚠️ No paths found in {svg_path}")
        return

    # Find bounding box
    min_x = min_y = float('inf')
    max_x = max_y = float('-inf')

    for path in paths:
        for segment in path:
            for point in segment:
                x, y = point.real, point.imag
                min_x = min(min_x, x)
                max_x = max(max_x, x)
                min_y = min(min_y, y)
                max_y = max(max_y, y)

    width  = max_x - min_x
    height = max_y - min_y

    if width == 0 or height == 0:
        print(f"⚠️ Empty path in {svg_path}")
        return

    # Dynamic scale to fit TARGET_HEIGHT
    scale_factor = TARGET_HEIGHT / height

    offset = complex(-min_x, -min_y)

    pen = glyph.getPen()

    for path in paths:
        first = True
        for segment in path:
            segment = segment.translated(offset)
            # segment = segment.scaled(scale_factor, -scale_factor)  # Flip Y
            # segment = segment.translated(complex(0, TARGET_HEIGHT))  # Shift up

            if isinstance(segment, Line):
                for point in segment:
                    x, y = point.real, point.imag
                    if first:
                        pen.moveTo((x, y))
                        first = False
                    else:
                        pen.lineTo((x, y))

            elif isinstance(segment, QuadraticBezier):
                p0 = segment.start
                p1 = segment.control
                p2 = segment.end
                curve_points = subdivide_quadratic(
                    (p0.real, p0.imag),
                    (p1.real, p1.imag),
                    (p2.real, p2.imag),
                    steps=32
                )
                if first:
                    pen.moveTo(curve_points[0])
                    first = False
                for pt in curve_points[1:]:
                    pen.lineTo(pt)

            elif isinstance(segment, CubicBezier):
                p0 = segment.start
                p1 = segment.control1
                p2 = segment.control2
                p3 = segment.end
                curve_points = subdivide_cubic(
                    (p0.real, p0.imag),
                    (p1.real, p1.imag),
                    (p2.real, p2.imag),
                    (p3.real, p3.imag),
                    steps=16
                )
                if first:
                    pen.moveTo(curve_points[0])
                    first = False
                for pt in curve_points[1:]:
                    pen.lineTo(pt)

        pen.closePath()

    # Set glyph width based on SVG width
    glyph.width = int(width * scale_factor)  # 100 units padding

def build_font():
    # Check and delete existing directories/files if present
    if os.path.exists('master__ttf'):
        shutil.rmtree('master__ttf')
        print("Deleted existing 'master__ttf' folder.")
    if os.path.exists(f"{FONT_NAME}.ufo"):
        shutil.rmtree(f"{FONT_NAME}.ufo")
        print(f"Deleted existing '{FONT_NAME}.ufo' folder.")

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
            fn   = f"{ch}{i}.svg"
            path = os.path.join(IMAGE_FOLDER, fn)
            if not os.path.exists(path):
                print(f"❌ Missing {fn}")
                continue

            glyph_name = ch if i == 1 else f"{ch}.alt{i-1}"
            glyph = ufo.newGlyph(glyph_name)
            if i == 1:
                glyph.unicodes = [ord(ch)]

            svg_to_glyph(glyph, path)
            print(f"✅ Added {glyph_name}")

            if i > 1:
                alt_names.append(glyph_name)

        for alt in alt_names:
            feature_lines.append(f"sub {ch}' by {alt};")

    ufo.features.text = (
        "feature calt {\n    " +
        "\n    ".join(feature_lines) +
        "\n} calt;\n"
    )

    space = ufo.newGlyph("space")
    space.unicodes = [ord(' ')]
    space.width = 500
    print("✅ Added wide space glyph")

    ufo_path = f"{FONT_NAME}.ufo"
    ufo.save(ufo_path)

    project = FontProject()
    project.build_ttfs([ufo])
    print(f"\n🎉 Done — {FONT_NAME}-Regular.ttf generated")

if __name__ == "__main__":
    build_font()
